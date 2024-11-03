import streamlit as st
import pandas as pd
import datetime as dt
import requests
import json
import time
from apscheduler.schedulers.background import BackgroundScheduler
from streamlit_cookies_controller import CookieController
from user_settings import save_user_settings

cookie_controller = CookieController()
if "auth_status" in cookie_controller.getAll():
    for k, v in cookie_controller.get("auth_status").items():
        st.session_state[k] = v

# Initialize scheduler
scheduler = BackgroundScheduler()

# Remove Streamlit hamburger (& any other elements)
st.markdown("""
<style>
.st-emotion-cache-yfhhig.ef3psqc5
{
visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


def query_check():
    valid = True

    if not st.session_state.user_id.isdigit():
        st.write("Error: user id must be an integer.")
        valid = False

    if st.session_state.game_tag.capitalize() not in (
            "Action", "Indie", "Adventure", "Casual", "RPG", "Strategy", "Simulation", "Early Access", "Free to Play",
            "Sports", "All"):
        st.write("Error: invalid game tag.")
        valid = False

    # Check scheduled_time is a valid time object
    if not isinstance(st.session_state.scheduled_time_g, dt.time):
        col1.write("Error: invalid time format.")
        valid = False

    if valid:
        st.write("Query is valid!")
    else:
        st.write("Please fix the errors mentioned above.")
        st.session_state.running = False
        time.sleep(5)
        st.rerun()

    return True


def start_watcher():
    """Function to schedule the watcher."""
    if scheduler.running:
        scheduler.start()
    # Ensure only one job is scheduled (if needed)
    if scheduler.get_jobs():
        scheduler.add_job(
            personal_watcher,
            'cron',
            hour=st.session_state.scheduled_time_w.hour,
            minute=st.session_state.scheduled_time_w.minute,
            day_of_week=','.join(st.session_state.selected_days_cron_g)
        )

    col1.write("Waiting for the scheduled task to run...")


def personal_watcher():
    """The function that watches the wishlist."""
    page = 0
    game_number = 1
    columns = ["Game Name", "Discount", "Discounted Price", "Game Tags", "Game Link"]
    games_list = []

    while True:
        url = F"https://store.steampowered.com/wishlist/profiles/{st.session_state.user_id}/wishlistdata/?p={page}&v="
        response = requests.get(url)

        if response.status_code == 200:
            games_data = json.loads(response.text)
            if games_data:
                for game_id, game_info in games_data.items():
                    game_name = game_info.get("name")
                    game_price = game_info["subs"][0].get("price") if game_info.get("subs") else "N/A"
                    game_discount = game_info["subs"][0].get("discount_pct") if game_info.get("subs") else "N/A"
                    game_tags = game_info.get("tags")

                    game_data = None
                    if st.session_state.game_tag in game_tags or st.session_state.game_tag == "All":
                        if game_discount != "N/A":
                            game_data = [game_name, game_discount, game_price, game_tags,
                                         F"https://store.steampowered.com/app/{game_id}"]
                            game_number += 1
                            if game_data:
                                games_list.append(game_data)

                page += 1
            else:
                st.write("Search end")
                break
        else:
            st.write(f"Query error: {response.status_code}")
            break

    df = pd.DataFrame(games_list, columns=columns)
    df.index = range(1, len(df) + 1)
    st.dataframe(df)


day_mapping_reverse = {
    'mon': 'Monday',
    'tue': 'Tuesday',
    'wed': 'Wednesday',
    'thu': 'Thursday',
    'fri': 'Friday',
    'sat': 'Saturday',
    'sun': 'Sunday'
}

# Genre list
genres = ["Action", "Indie", "Adventure", "Casual", "RPG", "Strategy", "Simulation", "Early Access", "Free to Play",
          "Sports"]
genres_df = pd.DataFrame({'Genre': genres}, index=list(range(1, len(genres) + 1)))

# Initialize session state
if 'running' not in st.session_state:
    st.session_state.running = False

# Columns for UI
col1, col2 = st.columns(2)
col2.table(genres_df)

if st.session_state.running:
    col1.write("<h4>Watcher is running</h4>", unsafe_allow_html=True)
    personal_watcher()
    if col1.button("Reset watcher"):
        st.session_state.running = False
        st.rerun()
else:
    col1.write("<h4>Watcher is not running</h4>", unsafe_allow_html=True)
    st.session_state["user_id"] = col1.text_input("Enter user SteamID64(ex., 76561198120742945):",
                                                  value=st.session_state["user_id"])
    st.session_state["game_tag"] = col1.text_input("Enter game genre:", value=st.session_state["game_tag"])

    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    selected_days_w = col1.multiselect("Select the days of the week:", days_of_week,
                                     default=st.session_state.selected_days_w)
    day_mapping = {
        'Monday': 'mon',
        'Tuesday': 'tue',
        'Wednesday': 'wed',
        'Thursday': 'thu',
        'Friday': 'fri',
        'Saturday': 'sat',
        'Sunday': 'sun'
    }
    st.session_state.selected_days_cron_w = [day_mapping[day] for day in
                                             selected_days_w]  # convert selected days to cron format
    scheduled_time_w = col1.time_input("Select the time to run the task (e.g., 14:30):",
                                                      value=st.session_state.scheduled_time_w, step=300)

    with col1:
        subcol1, subcol2 = st.columns(2)

        if subcol1.button("Save settings"):
            st.session_state.selected_days_w = selected_days_w
            st.session_state.scheduled_time_w = scheduled_time_w
            if query_check():
                save_user_settings(st.session_state.username)
            else:
                st.write("query check is not successfull")
        if subcol2.button("Run watcher now"):
            query_check()
            st.session_state.running = True
            time.sleep(2)
            st.rerun()

# Initializing state and tracking reload
if "page_reloaded" not in st.session_state:
    st.session_state["page_reloaded"] = False

# State check and single reload
if not st.session_state["page_reloaded"]:
    st.session_state["page_reloaded"] = True
    st.rerun()

