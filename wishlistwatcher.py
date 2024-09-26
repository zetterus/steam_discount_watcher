import streamlit as st
import pandas as pd
import datetime as dt
import requests
import json
import time
from apscheduler.schedulers.background import BackgroundScheduler

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
        if not (0 <= st.session_state.scheduled_time.hour < 24) or not (0 <= st.session_state.scheduled_time.minute < 60):
            raise ValueError("Invalid time.")
    except ValueError:
        st.write("Error: time is invalid.")
        valid = False

    if valid:
        st.session_state.running = True
        st.write("Query seems valid!")
    else:
        st.write("Please fix the errors mentioned above.")
        st.session_state.running = False
        # time.sleep(5)
        # st.rerun()


def start_watcher():
    scheduler.add_job(
        personal_watcher,
        'cron',
        hour=st.session_state.scheduled_time.hour,
        minute=st.session_state.scheduled_time.minute,
        day_of_week=','.join(st.session_state.selected_days_cron)  # Format: 'mon,tue,wed'
    )
    scheduler.start()


def personal_watcher():
    # Starting page number
    page = 0
    game_number = 1

    # dataframe headers
    columns = ["№", "Game Name", "Discount", "Discounted Price", "Game Tags", "Game Link"]

    # games list initialization
    games_list = []

    # adding games to list
    while True:
        # formating url for each page
        url = F"https://store.steampowered.com/wishlist/profiles/{st.session_state.user_id}/wishlistdata/?p={page}&v="

        # sending query to server
        response = requests.get(url)

        # response check
        if response.status_code == 200:

            games_data = json.loads(response.text)
            print(games_data)
            for game_id, game_info in games_data.items():
                game_name = game_info.get("name")
                game_price = game_info["subs"][0].get("price") if game_info.get("subs") else "N/A"
                game_discount = game_info["subs"][0].get("discount_pct") if game_info.get("subs") else "N/A"
                game_tags = game_info.get("tags")
                try:
                    if st.session_state.game_tag in game_tags or st.session_state.game_tag == "All":
                        if game_discount:
                            game_data = [game_number, game_name, game_discount, game_price, game_tags,
                                         F"https://store.steampowered.com/app/{game_id}"]
                            print(1, game_data)
                except:
                    st.write(game_name, "write error")
                    print(game_name, "write error")

                print(2, game_data)
                games_list.append(game_data)
                game_number += 1

            print(F"Page {page} processed.")  # TODO: убрать
            page += 1

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

    st.session_state.task_done = True


# app status checkup
if 'running' not in st.session_state:
    st.session_state.running = False

if 'task_done' not in st.session_state:
    st.session_state.task_done = False

if 'submit_btn_pressed' not in st.session_state:
    st.session_state.submit_btn_pressed = False

if 'run_btn_pressed' not in st.session_state:
    st.session_state.run_btn_pressed = False

# genres list
genres = ["Action", "Indie", "Adventure", "Casual", "RPG", "Strategy", "Simulation", "Early Access", "Free to Play",
          "Sports"]

# creating table from list
genres_df = pd.DataFrame({'Genre': genres}, index=list(range(1, len(genres) + 1)))

# columns
col1, col2 = st.columns(2)

# 2nd column
# genres ids
col2.table(genres_df)

# 1st column
# genre choose, discount, check time, check button
# app status display
if st.session_state.running:
    col1.write("<h4>Watcher is running</h4>", unsafe_allow_html=True)

    # Once the button is pressed, the form is hidden, but the task continues
    if st.session_state.submit_btn_pressed:
        col1.write("Watcher has been scheduled.")
        col1.write("Waiting for the scheduled task to run...")
        start_watcher()
    elif st.session_state.run_btn_pressed:
        col1.write("Watcher is running immediately...")
        personal_watcher()

else:
    col1.write("<h4>Watcher is not running</h4>", unsafe_allow_html=True)
    st.session_state.user_id = col1.text_input("Enter user SteamID64: 76561198120742945")
    st.session_state.game_tag = col1.text_input("Enter game genre:")
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    selected_days = col1.multiselect("Select the days of the week:", days_of_week, default=['Monday'])
    day_mapping = {
        'Monday': 'mon',
        'Tuesday': 'tue',
        'Wednesday': 'wed',
        'Thursday': 'thu',
        'Friday': 'fri',
        'Saturday': 'sat',
        'Sunday': 'sun'
    }
    st.session_state.selected_days_cron = [day_mapping[day] for day in
                                           selected_days]  # convert selected days to cron format
    st.session_state.scheduled_time = col1.time_input("Select the time to run the task (e.g., 14:30):",
                                                      value=dt.time(12, 0),
                                                      step=300)

    with col1:
        subcol1, subcol2 = st.columns(2)

        submit_btn = subcol1.button("Submit request")
        run_btn = subcol2.button("Run watcher now")

        # Manage button presses
        if submit_btn:
            query_check()
            st.session_state.submit_btn_pressed = True
            st.session_state.running = True  # Assuming the task starts running when the form is submitted
            col2.markdown("---")
            col2.write("Watcher successfully scheduled.")
            # time.sleep(5)
            # st.rerun()

        elif run_btn:
            query_check()
            st.session_state.run_btn_pressed = True
            st.session_state.running = True
            col2.markdown("---")
            col2.write("Watcher successfully started.")
            # time.sleep(5)
            # st.rerun()

    # while True:
    #     try:
    #         st.session_state.user_id = input("Enter user steam SteamID64:")  # 76561198120742945
    #         st.session_state.user_id == int(st.session_state.user_id)
    #         st.session_state.game_tag = input(
    #             "Action|Indie|Adventure|Casual|RPG|Strategy|Simulation|Early Access|Free to Play|Sports|All\nEnter game tag:")
    #         st.session_state.game_tag == str(st.session_state.game_tag)
    #         st.session_state.scheduled_time = input("Input check time(example 14:30):")
    #         0 < int(st.session_state.scheduled_time.split(":")[0]) < 24
    #         0 < int(st.session_state.scheduled_time.split(":")[1]) < 60
    #         st.write("Input accepted")
    #         break
    #     except:
    #         st.write("Invalid user.. input")
