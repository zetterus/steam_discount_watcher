import streamlit as st
import gspread
import streamlit_authenticator as stauth
from oauth2client.service_account import ServiceAccountCredentials
import bcrypt

# Define the scope for Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials from secrets.toml
creds_dict = st.secrets["gcp_service_account"]

# Authorize the client with credentials
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Open the Google Sheet
sheet = client.open("streamlit_watcher_credentials").sheet1

# Function to add a new user with hashed password and settings
def add_user_to_gsheet(username, email, name, password, settings_discount, settings_wishlist):
    # Hash the password using bcrypt
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    # Create user dictionary structure
    user_data = {
        'username': username,
        'email': email,
        'name': name,
        'password': hashed_password,
        'failed_login_attempts': 0,
        'logged_in': False,
        'settings_discount': settings_discount,
        'settings_wishlist': settings_wishlist
    }

    # Add the user data to the Google Sheet
    sheet.append_row([
        user_data['username'],
        user_data['email'],
        user_data['name'],
        user_data['password'],
        user_data['failed_login_attempts'],
        user_data['logged_in'],
        str(user_data['settings_discount']),
        str(user_data['settings_wishlist'])
    ])

    st.success("User added successfully!")

# Example usage to register a user
if st.button('Register New User'):
    # Example settings data for discount and wishlist (replace these values with actual data)
    settings_discount = {
        "game_tag_id": "113",
        "is_discounted_index": 1,
        "scheduled_time": "12:05",
        "selected_days_cron": ["mon", "fri", "sun"]
    }

    settings_wishlist = {
        "user_id": "76561198120742945",
        "game_tag": "Strategy",
        "scheduled_time": "12:30",
        "selected_days_cron": ["mon", "thu", "sat"]
    }

    add_user_to_gsheet(
        username="zetter",
        email="zetter.vitrolic@gmail.com",
        name="z x",
        password="yourpassword123",  # Plain text password
        settings_discount=settings_discount,
        settings_wishlist=settings_wishlist
    )

# Display current data from Google Sheet
st.write("Current users in the sheet:")
st.dataframe(sheet.get_all_records())
