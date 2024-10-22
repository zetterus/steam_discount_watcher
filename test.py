import time
import streamlit as st
import pandas as pd
import datetime as dt
from bs4 import BeautifulSoup
import requests
import json
from apscheduler.schedulers.background import BackgroundScheduler
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import os

# --- Google Sheets Setup ---

# Define the scope
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Add your credentials file (replace 'your-credentials.json' with your file name)
creds = ServiceAccountCredentials.from_json_keyfile_name("steam-watcher-credentials-db0622d10a00.json", scope)

# Authorize the client sheet
client = gspread.authorize(creds)

# Open the Google Sheet (replace 'your-google-sheet-name' with your sheet name)
sheet = client.open("streamlit_watcher_credentials").sheet1  # Use .sheet1 or specify the sheet name

# --- Streamlit and Authentication Setup ---

# Remove Streamlit hamburger (& any other elements)
st.markdown("""
<style>
.st-emotion-cache-yfhhig.ef3psqc5
{
visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# Load config file
with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Create the authenticator object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Authenticate user
name, authentication_status, username = authenticator.login(location='main', key="Login")

# result = authenticator.login(location='main', key="Login")
#
# st.write(f"Result of login: {result}")

if authentication_status:
    st.write(f'Welcome **{name}**')

    # Logout button
    if st.button('Logout'):
        authenticator.logout('Logout', 'main')
        st.session_state.clear()
        st.experimental_rerun()

    # --- User Registration ---

    st.header("Register a New User")

    try:
        # Registration form
        with st.form('Register User'):
            new_username = st.text_input('Username')
            new_name = st.text_input('Name')
            new_email = st.text_input('Email')
            new_password = st.text_input('Password', type='password')
            confirm_password = st.text_input('Confirm Password', type='password')
            submitted = st.form_submit_button('Register')

            if submitted:
                if new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    # Check if user already exists in Google Sheets
                    users = sheet.get_all_records()
                    usernames = [user['username'] for user in users]

                    if new_username in usernames:
                        st.warning('User already exists.')
                    else:
                        # Hash the password
                        hashed_password = stauth.Hasher([new_password]).generate()[0]

                        # Append new user to Google Sheet
                        new_user = [new_username, new_name, new_email, hashed_password]
                        sheet.append_row(new_user)

                        st.success('User registered successfully!')

    except Exception as e:
        st.error(f"An error occurred: {e}")

    # --- Rest of your application code ---

elif authentication_status is False:
    st.error('Username/password is incorrect')

elif authentication_status is None:
    st.warning('Please enter your username and password')
