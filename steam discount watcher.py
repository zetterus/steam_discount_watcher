import streamlit as st
import pandas as pd
import datetime as dt
from bs4 import BeautifulSoup
import requests
import json
import schedule
import time


# #remove streamlit hamburger (& any other elements)
# st.markdown("""
# <style>
# .st-emotion-cache-yfhhig.ef3psqc5
# {
# visibility: hidden;
# }
# </style>
# """, unsafe_allow_html=True)
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
    global game_tag_id, is_discounted, scheduled_time  # Access global variables

    valid = True  # Flag to indicate valid input

    # Check game_tag_id is an integer
    try:
        game_tag_id = int(game_tag_id)
    except ValueError:
        st.write("Error: game tag id must be an integer.")
        valid = False

    # Check is_discounted is either "yes" or "no"
    if is_discounted not in ("yes", "no"):
        st.write("Error: discount option must be 'yes' or 'no'.")
        valid = False

    # Check scheduled_time is a valid time object
    if not isinstance(scheduled_time, dt.time):
        st.write("Error: invalid time format. Please use the time picker.")
        valid = False

    if valid:
        st.write("Query seems valid!")
    else:
        st.write("Please fix the errors mentioned above.")
        # You can optionally clear the input fields here for a better user experience.


st.markdown("<h4 style='text-align: center;'>WARNING! Frequent usage may cause block. Use at your own risk.</h4>",
            unsafe_allow_html=True)
st.markdown("---")

genres_df = pd.DataFrame({
    "genres": ["Action", "Indie", "Adventure", "Casual", "RPG", "Strategy", "Simulation", "Early Access",
               "Free to Play", "Sports"],
    "game_id": [19, 492, 21, 597, 122, 9, 599, 493, 113, 701]
})

# columns
col1, col2 = st.columns(2)

# 1st column
# genres ids and genre choose
col1.table(genres_df.set_index(genres_df.columns[0]))
game_tag_id = col1.text_input("Enter game tag id:")
with col1:
    subcol1, subcol2 = st.columns(2)
    submit_btn = subcol1.button("Submit request", on_click=query_check)
    run_btn = subcol2.button("Run watcher now")

# 2nd column
# discount, check time, check button
is_discounted = col2.radio("Search for discounted?", options=("yes", "no"))
scheduled_time = col2.time_input("Input check time(example 14:30):", value=dt.time(12, 0), step=300)
