import time
import streamlit as st
import pandas as pd
import datetime as dt
from bs4 import BeautifulSoup
import requests
import json
from apscheduler.schedulers.background import BackgroundScheduler
from streamlit_cookies_controller import CookieController
from user_settings import save_user_settings

cookie_controller = CookieController()
if "auth_status" in cookie_controller.getAll():
    for k, v in cookie_controller.get("auth_status").items():
        st.session_state[k] = v

scheduler = BackgroundScheduler()

# remove streamlit hamburger (& any other elements)
st.markdown("""
<style>
.st-emotion-cache-yfhhig.ef3psqc5
{
visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# # completely removes header
# .st-emotion-cache-h4xjwg.ezrtsby2
# {
# visibility: hidden;
# }

# query check
def query_check():
    """
    This function checks the validity of user input and displays messages accordingly.
    """

    valid = True  # Flag to indicate valid input

    # Check game_tag_id is an integer
    if not st.session_state.game_tag_id.isdigit():
        col1.write("Error: game tag id must be an integer.")
        valid = False

    # Check is_discounted is either "yes" or "no"
    if st.session_state.is_discounted not in ("yes", "no"):
        col1.write("Error: discount option must be 'yes' or 'no'.")
        valid = False

    # Check scheduled_time is a valid time object
    if not isinstance(st.session_state.scheduled_time_g, dt.time):
        col1.write("Error: invalid time format.")
        valid = False

    if valid:
        # st.session_state.running = True
        col2.write("Query seems valid!")
    else:
        col1.write("Please fix the errors mentioned above.")
        st.session_state.running = False
        time.sleep(5)
        st.rerun()

    return True


# run watcher through planner function
def start_watcher():
    # global scheduled_time, selected_days
    scheduler.add_job(
        watcher,
        'cron',
        hour=st.session_state.scheduled_time_g.hour,
        minute=st.session_state.scheduled_time_g.minute,
        day_of_week=','.join(st.session_state.selected_days_cron_g)  # Format: 'mon,tue,wed'
    )
    scheduler.start()


def watcher():
    # Starting page number
    page_number = 0
    page_count = 100  # Games quantity per page, no more than 100?
    game_number = 1

    # games list initialization
    games_list = []

    # adding games to list
    while True:
        # formating url for each page
        url = f"https://store.steampowered.com/search/results/?query&start={page_number}&count={page_count}&dynamic_data=&sort_by=_ASC&tags={st.session_state.game_tag_id}&snr=1_7_7_2300_7&specials={st.session_state.is_discounted}&infinite=1"

        # sending query to server
        response = requests.get(url)

        # response check
        if response.status_code == 200:
            # JSON reply parsing
            data = json.loads(response.text)

            # extracting HTML by key "results_html"
            results_html = data.get('results_html', '')

            # if no results found cycle ends
            if results_html == "\r\n<!-- List Items -->\r\n<!-- End List Items -->\r\n":
                break

            #  HTML parsing with BeautifulSoup
            soup = BeautifulSoup(results_html, 'html.parser')
            games_found = soup.find_all("a", class_="search_result_row")

            for game in games_found:
                game_name = game.find("span", class_="title").text
                game_link = game.get("href")
                try:
                    game_discount = game.find("div", class_="discount_pct").text
                    discount_original_price = game.find("div", class_="discount_original_price").text
                    discount_final_price = game.find("div", class_="discount_final_price").text
                    game_data = [game_number, game_name, game_discount, discount_final_price, discount_original_price,
                                 game_link]
                except:
                    game_data = [game_number, game_name, "N/A", "N/A", "N/A", game_link]

                game_number += 1
                games_list.append(game_data)

            # continue to next page
            page_number += page_count
            print(F"Page {str(page_number)[:2]} completed.")
        else:
            st.write(f"Query error: {response.status_code}")
            break

    # creating dataframe
    df = pd.DataFrame(games_list,
                      columns=["№", "Game Name", "Discount", "Discounted Price", "Original Price", "Game Link"])

    # changing index to start from 1
    df.index = range(1, len(df) + 1)

    # display DataFrame in Streamlit
    st.dataframe(df)


genres_df = pd.DataFrame({
    "genres": ["Action", "Indie", "Adventure", "Casual", "RPG", "Strategy", "Simulation", "Early Access",
               "Free to Play", "Sports"],
    "game_id": [19, 492, 21, 597, 122, 9, 599, 493, 113, 701]
})

# columns
col1, col2 = st.columns(2)

# 2nd column
# genres ids
col2.table(genres_df.set_index(genres_df.columns[0]))

day_mapping_reverse = {
    'mon': 'Monday',
    'tue': 'Tuesday',
    'wed': 'Wednesday',
    'thu': 'Thursday',
    'fri': 'Friday',
    'sat': 'Saturday',
    'sun': 'Sunday'
}

# Initialize session state
if 'running' not in st.session_state:
    st.session_state.running = False

# 1st column
# genre choose, discount, check time, check button
# app status display
if st.session_state.running:
    col1.write("<h4>Watcher is running</h4>", unsafe_allow_html=True)
    watcher()
    if col1.button("Reset watcher"):
        st.session_state.running = False
        st.rerun()
else:
    col1.write("<h4>Watcher is not running</h4>", unsafe_allow_html=True)
    st.session_state.game_tag_id = col1.text_input("Enter game tag id:", value=st.session_state["game_tag_id"])
    is_discounted = col1.radio("Search for discounted?", options=("yes", "no"),
                               index=st.session_state["is_discounted_index"])
    st.session_state.is_discounted_index = 0 if is_discounted == "yes" else 1
    # days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    # selected_days_g = col1.multiselect("Select the days of the week:", days_of_week,
    #                                  default=st.session_state["selected_days_g"])
    # day_mapping = {
    #     'Monday': 'mon',
    #     'Tuesday': 'tue',
    #     'Wednesday': 'wed',
    #     'Thursday': 'thu',
    #     'Friday': 'fri',
    #     'Saturday': 'sat',
    #     'Sunday': 'sun'
    # }
    # st.session_state.selected_days_cron_g = [day_mapping[day] for day in
    #                                          selected_days_g]  # convert selected days to cron format
    # scheduled_time_g = col1.time_input("Select the time to run the task (e.g., 14:30):",
    #                                                      value=st.session_state.scheduled_time_g, step=300)


    with col1:
        subcol1, subcol2 = st.columns(2)

        # Manage button presses
        if subcol1.button("Save settings"):
            st.session_state.selected_days_g = selected_days_g
            st.session_state.scheduled_time_g = scheduled_time_g
            if query_check():
                save_user_settings(st.session_state.username)
            else:
                st.write("query_check not succesfull")
        if subcol2.button("Run watcher now"):
            query_check()
            st.session_state.running = True
            col2.markdown("---")
            col2.write("Watcher successfully started.")
            time.sleep(1)
            st.rerun()


# Initializing state and tracking reload
if "page_reloaded" not in st.session_state:
    st.session_state["page_reloaded"] = False

# State check and single reload
if not st.session_state["page_reloaded"]:
    st.session_state["page_reloaded"] = True
    st.rerun()
