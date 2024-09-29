import streamlit as st
import pandas as pd
import datetime as dt
import requests
import json
import time
from apscheduler.schedulers.background import BackgroundScheduler

# Initialize scheduler
scheduler = BackgroundScheduler()
if not scheduler.running:
    scheduler.start()

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

    try:
        if not (0 <= st.session_state.scheduled_time.hour < 24) or not (
                0 <= st.session_state.scheduled_time.minute < 60):
            raise ValueError("Invalid time.")
    except ValueError:
        st.write("Error: time is invalid.")
        valid = False

    if valid:
        st.session_state.running = True
        st.write("Query is valid!")
    else:
        st.write("Please fix the errors mentioned above.")
        st.session_state.running = False
        st.rerun()


def start_watcher():
    """Function to schedule the watcher."""
    # if not scheduler.running:
    #     scheduler.start()

    # Ensure only one job is scheduled (if needed)
    if not scheduler.get_jobs():
        scheduler.add_job(
            personal_watcher,
            'cron',
            hour=st.session_state.scheduled_time.hour,
            minute=st.session_state.scheduled_time.minute,
            day_of_week=','.join(st.session_state.selected_days_cron)
        )
    col1.write("Watcher scheduled successfully!")


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


# Initialize session state
if 'running' not in st.session_state:
    st.session_state.running = False
if 'submit_btn_pressed' not in st.session_state:
    st.session_state.submit_btn_pressed = False
if 'run_btn_pressed' not in st.session_state:
    st.session_state.run_btn_pressed = False

# Genre list
genres = ["Action", "Indie", "Adventure", "Casual", "RPG", "Strategy", "Simulation", "Early Access", "Free to Play",
          "Sports"]
genres_df = pd.DataFrame({'Genre': genres}, index=list(range(1, len(genres) + 1)))

# Columns for UI
col1, col2 = st.columns(2)
col2.table(genres_df)

if st.session_state.running:
    col1.write("<h4>Watcher is running</h4>", unsafe_allow_html=True)
    if st.session_state.submit_btn_pressed:
        col1.write("Waiting for the scheduled task to run...")
        start_watcher()
    elif st.session_state.run_btn_pressed:
        col1.write("Watcher is running immediately...")
        personal_watcher()
    if col1.button("Restart Watcher"):
        st.session_state.clear()
        st.rerun()
else:
    col1.write("<h4>Watcher is not running</h4>", unsafe_allow_html=True)
    st.session_state.user_id = col1.text_input("Enter user SteamID64: 76561198120742945")
    st.session_state.game_tag = col1.text_input("Enter game genre:")

    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    selected_days = col1.multiselect("Select the days of the week:", days_of_week, default=['Monday'])
    day_mapping = {'Monday': 'mon', 'Tuesday': 'tue', 'Wednesday': 'wed', 'Thursday': 'thu', 'Friday': 'fri',
                   'Saturday': 'sat', 'Sunday': 'sun'}
    st.session_state.selected_days_cron = [day_mapping[day] for day in selected_days]
    st.session_state.scheduled_time = col1.time_input("Select the time to run the task (e.g., 14:30):",
                                                      value=dt.time(12, 0), step=300)

    with col1:
        subcol1, subcol2 = st.columns(2)
        submit_btn = subcol1.button("Submit request")
        run_btn = subcol2.button("Run watcher now")

        if submit_btn:
            query_check()
            st.session_state.submit_btn_pressed = True
            st.session_state.running = True
            time.sleep(2)
            st.rerun()

        elif run_btn:
            query_check()
            st.session_state.run_btn_pressed = True
            st.session_state.running = True
            time.sleep(2)
            st.rerun()
