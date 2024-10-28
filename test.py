import streamlit as st
import streamlit_authenticator as stauth
import gspread
import yaml
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
from yaml.loader import SafeLoader
import bcrypt

# Define the scope for Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials from secrets.toml
creds_dict = st.secrets["gcp_service_account"]

# Use the credentials from `st.secrets`
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)

# Authorize the client sheet
client = gspread.authorize(creds)

# Open the Google Sheet using the URL or spreadsheet name from `secrets.toml`
spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
sheet = client.open_by_url(spreadsheet_url).sheet1


def load_credentials_from_sheet(username=None):
    users = sheet.get_all_records()  # Get all existing user data
    credentials = {"usernames": {}}

    for user in users:
        if user["username"] == username:
            settings_discount = yaml.load(user["settings_discount"], Loader=SafeLoader)
            settings_wishlist = yaml.load(user["settings_wishlist"], Loader=SafeLoader)
            credentials["usernames"][username] = {
                "email": user["email"],
                "name": user["name"],
                "password": user["password"],  # Ensure passwords are already hashed
                "failed_login_attempts": user.get("failed_login_attempts", 0),
                "logged_in": user.get("logged_in", 0),
                "settings_discount": {
                    "game_tag_id": settings_discount.get("game_tag_id", ""),
                    "is_discounted_index": settings_discount.get("is_discounted_index", 0),
                    "scheduled_time": settings_discount.get("scheduled_time", "12:00"),
                    "selected_days_cron": settings_discount.get("selected_days_cron", ""),
                },
                "settings_wishlist": {
                    "user_id": settings_wishlist.get("user_id", ""),
                    "game_tag": settings_wishlist.get("game_tag", ""),
                    "scheduled_time": settings_wishlist.get("scheduled_time", "12:00"),
                    "selected_days_cron": settings_wishlist.get("selected_days_cron", ""),
                },
            }
            return credentials  # Return immediately once user is found

    # If user is not found, log an error and return an empty dictionary
    st.error("No user record found")
    return credentials


cred = load_credentials_from_sheet()

st.write(cred)
st.write(st.session_state)

