import yaml
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import datetime as dt
import os
from streamlit_authenticator.utilities import (CredentialsError,
                                               ForgotError,
                                               Hasher,
                                               LoginError,
                                               RegisterError,
                                               ResetError,
                                               UpdateError)

# Default settings for new users
DEFAULT_DISCOUNT_SETTINGS = {
    "game_tag_id": "0",
    "is_discounted_index": 0,
    "scheduled_time": "12:00",
    "selected_days_cron": ["mon", "wed", "fri"],
}

DEFAULT_WISHLIST_SETTINGS = {
    "user_id": "",
    "game_tag": "",
    "scheduled_time": "12:00",
    "selected_days_cron": ["tue", "thu", "sat"],
}

# Define the scope for Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Use the credentials from `st.secrets`
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)

# Authorize the client sheet
client = gspread.authorize(creds)

# Open the Google Sheet using the URL or spreadsheet name from `secrets.toml`
spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
sheet = client.open_by_url(spreadsheet_url).sheet1


# Define the function to load data from Google Sheets and apply settings based on current file
def load_and_apply_settings_to_widgets(username, current_filename):
    user_settings = get_user_from_gsheet(username)

    if user_settings:
        if current_filename == "steamdiscountwatcher.py":
            st.session_state["game_tag_id"] = user_settings.get("settings_discount", {}).get("game_tag_id", "")
            st.session_state["is_discounted_index"] = user_settings.get("settings_discount", {}).get(
                "is_discounted_index", 0)
            st.session_state["selected_days_cron"] = user_settings.get("settings_discount", {}).get(
                "selected_days_cron", [])
            scheduled_time = user_settings.get("settings_discount", {}).get("scheduled_time", "12:00")
            st.session_state["scheduled_time"] = dt.datetime.strptime(scheduled_time, "%H:%M").time()

        elif current_filename == "wishlistwatcher.py":
            st.session_state["user_id"] = user_settings.get("settings_wishlist", {}).get("user_id", "")
            st.session_state["game_tag"] = user_settings.get("settings_wishlist", {}).get("game_tag", "")
            st.session_state["selected_days_cron"] = user_settings.get("settings_wishlist", {}).get(
                "selected_days_cron", [])
            scheduled_time = user_settings.get("settings_wishlist", {}).get("scheduled_time", "12:00")
            st.session_state["scheduled_time"] = dt.datetime.strptime(scheduled_time, "%H:%M").time()
        else:
            st.write("Error: can't apply settings.")
    else:
        st.write("No settings found for the user.")


def session_state_to_dict(session_state):
    # Convert SessionStateProxy object to a dictionary
    data = {}
    for key, value in session_state.items():
        # Handle different data types appropriately
        data[key] = value
    return {st.session_state: data}


# Custom deserialization function
def dict_to_session_state(data):
    # Convert dictionary back to a SessionStateProxy object
    session_state = st.session_state
    for key, value in data.items():
        # Set values in SessionStateProxy
        session_state[key] = value
    return session_state


def upsert_user_data(username, name, email, hashed_password, settings_discount=None, settings_wishlist=None):
    users = sheet.get_all_records()  # Get all existing user data
    user_exists = False
    row_index = 0  # Variable to track the row index if the user is found

    # Search for the username in existing records
    for i, user in enumerate(users, start=2):  # Start at row 2 for data rows
        if user["username"] == username:
            user_exists = True
            row_index = i
            break

    # Prepare the data for the user
    user_row = [username, name, email, hashed_password, str(settings_discount or {}), str(settings_wishlist or {})]

    # Update if user exists, or append if not
    if user_exists:
        # Overwrite the row if user exists
        sheet.update(f'A{row_index}:H{row_index}', [user_row])
        st.success(f"Updated data for user '{username}'.")
    else:
        # Append a new row if user does not exist
        sheet.append_row(user_row)
        st.success(f"Added new user '{username}'.")


def get_user_from_gsheet(username):
    # Get all records from the sheet
    users = sheet.get_all_records()

    # Search for the username in the records
    for user in users:
        if user["username"] == username:
            return user

    # Return None if user is not found
    return None


def get_user_data(username):
    """Fetches and structures data for the specified username from Google Sheets."""
    records = sheet.get_all_records()  # Fetch all user data
    for record in records:
        if record["username"] == username:
            # Deserialize YAML for settings
            settings_discount = yaml.load(record.get("settings_discount", "{}"), Loader=SafeLoader)
            settings_wishlist = yaml.load(record.get("settings_wishlist", "{}"), Loader=SafeLoader)

            return {
                "email": record["email"],
                "name": record["name"],
                "password": record["password"],  # Password should be hashed
                "failed_login_attempts": record.get("failed_login_attempts", 0),
                "logged_in": record.get("logged_in", False),
                "settings_discount": settings_discount or {},
                "settings_wishlist": settings_wishlist or {}
            }
    return None


def load_credentials_from_sheet():
    """Loads and structures credentials from Google Sheets."""
    credentials = {"usernames": {}}

    # Retrieve all user records from Google Sheets
    users = sheet.get_all_records()

    for user in users:
        username = user["username"]
        credentials["usernames"][username] = {
            "email": user["email"],
            "name": user["name"],
            "password": user["password"],  # Ensure passwords are hashed
            "failed_login_attempts": user.get("failed_login_attempts", 0),
            "logged_in": user.get("logged_in", False),
            "settings_discount": yaml.load(user.get("settings_discount", "{}"), Loader=SafeLoader),
            "settings_wishlist": yaml.load(user.get("settings_wishlist", "{}"), Loader=SafeLoader),
        }

    return credentials


# Fetching the credentials and creating config dictionary
credentials = load_credentials_from_sheet()
config = {
    "credentials": credentials,
    "cookie": {
        "name": "auth_cookie",
        "key": "some_secret_key",
        "expiry_days": 30,
    }
}

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

# Authenticating user
if st.session_state['authentication_status']:
    st.write(f'Welcome **{st.session_state["name"]}**')

    if authenticator.logout():
        st.session_state.clear()
        st.rerun()

    try:

        # Fetch user data once
        try:
            user_data = get_user_data(st.session_state["username"])
        except Exception as e:
            st.error(f"Failed to load user data: {e}")

        st.write(user_data)
        st.write("Your genre watcher settings",
                 user_data["credentials"]["usernames"][st.session_state['username']]["settings_discount"])
    except:
        st.write("No genre watcher settings stored")
    try:
        st.write("Your wishlist watcher settings",
                 user_data["credentials"]["usernames"][st.session_state['username']]["settings_wishlist"])
    except:
        st.write("No wishlist watcher settings stored")

    # Creating a password reset widget
    if st.session_state['authentication_status']:
        try:
            if authenticator.reset_password(st.session_state['username']):
                st.success('Password modified successfully')
        except (CredentialsError, ResetError) as e:
            st.error(e)

elif st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect')

    # Creating a login widget
    try:
        authenticator.login()
        load_and_apply_settings_to_widgets(st.session_state["username"], os.path.basename(__file__))
    except Exception as e:
        st.write(e)

elif st.session_state['authentication_status'] is None:
    st.warning('Please enter your username and password')

    # Creating a login widget
    try:
        authenticator.login()
        load_and_apply_settings_to_widgets(st.session_state["username"], os.path.basename(__file__))
    except Exception as e:
        st.write(e)

    # Registration widget
    if not st.session_state.get("authentication_status"):
        try:
            email, username, name = authenticator.register_user(captcha=False, clear_on_submit=True)

            if email:
                st.success("User registered successfully!")

                # Hash the password
                hashed_password = stauth.Hasher([email]).generate()[0]

                # Prepare the data for Google Sheets
                new_user_data = [
                    username,
                    email,
                    name,
                    hashed_password,
                    0,  # failed_login_attempts
                    False,  # logged_in status
                    yaml.dump(DEFAULT_DISCOUNT_SETTINGS),  # Dump default settings to YAML format
                    yaml.dump(DEFAULT_WISHLIST_SETTINGS)
                ]

                # Append the new user data to Google Sheets
                sheet.append_row(new_user_data)
                st.success("User credentials saved to Google Sheets with default settings.")

        except RegisterError as e:
            st.error(e)
