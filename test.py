import time
import streamlit as st
import pandas as pd
import datetime as dt
from bs4 import BeautifulSoup
import requests
import json
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

# set page title
st.set_page_config(page_title="Steam discount watcher")

# Remove streamlit hamburger (& any other elements)
st.markdown("""
<style>
.st-emotion-cache-yfhhig.ef3psqc5 {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# app status checkup
if 'running' not in st.session_state:
    st.session_state.running = False

if 'task_done' not in st.session_state:
    st.session_state.task_done = False

if 'submit_btn_pressed' not in st.session_state:
    st.session_state.submit_btn_pressed = False

if 'run_btn_pressed' not in st.session_state:
    st.session_state.run_btn_pressed = False

genres_df = pd.DataFrame({
    "genres": ["Action", "Indie", "Adventure", "Casual", "RPG", "Strategy", "Simulation", "Early Access",
               "Free to Play", "Sports"],
    "game_id": [19, 492, 21, 597, 122, 9, 599, 493, 113, 701]
})

# columns
col1, col2 = st.columns(2)

# 2nd column: Display genres
col2.table(genres_df.set_index(genres_df.columns[0]))

# 1st column: Manage task running status and input visibility
if st.session_state.running:
    col1.write("<h4>Watcher is running</h4>", unsafe_allow_html=True)

    if st.session_state.task_done:
        col1.button("Watcher task completed! Click to restart.")

else:
    col1.write("<h4>Watcher is not running</h4>", unsafe_allow_html=True)

    # Display form elements only if neither button has been pressed
    if not st.session_state.submit_btn_pressed and not st.session_state.run_btn_pressed:
        st.session_state.game_tag_id = col1.text_input("Enter game tag id:")
        st.session_state.is_discounted = col1.radio("Search for discounted?", options=("yes", "no"), index=0)

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
                                                          value=dt.time(12, 0), step=300)

        with col1:
            subcol1, subcol2 = st.columns(2)

            submit_btn = subcol1.button("Submit request")
            run_btn = subcol2.button("Run watcher now")

            # Manage button presses
            if submit_btn:
                st.session_state.submit_btn_pressed = True
                st.session_state.running = True  # Assuming the task starts running when the form is submitted
                col2.markdown("---")
                col2.write("Watcher successfully scheduled.")
                time.sleep(1)
                st.rerun()

            elif run_btn:
                st.session_state.run_btn_pressed = True
                st.session_state.running = True
                col2.markdown("---")
                col2.write("Watcher successfully started.")
                time.sleep(1)
                st.rerun()

# Once the button is pressed, the form is hidden, but the task continues
if st.session_state.submit_btn_pressed:
    col1.write("Watcher has been scheduled.")
    col1.write("Waiting for the scheduled task to run...")
elif st.session_state.run_btn_pressed:
    col1.write("Watcher is running immediately...")
