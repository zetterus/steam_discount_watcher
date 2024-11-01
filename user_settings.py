import time
import datetime as dt
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from werkzeug.security import generate_password_hash, check_password_hash
import json

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(creds)
sheet = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"]).sheet1


# Utility functions
def get_user_data(username):
    """Fetch user data from Google Sheets by username."""
    users = sheet.get_all_records()
    for user in users:
        if user['username'] == username:
            return user
    return None


def register_user(username, email, name, password):
    """Register a new user in Google Sheets."""
    if get_user_data(username):
        st.warning("User already exists.")
    else:
        password_hash = generate_password_hash(password)
        new_user_data = {
            "username": username,
            "email": email,
            "name": name,
            "password_hash": password_hash,
            "settings_discount": json.dumps({}),
            "settings_wishlist": json.dumps({})
        }
        sheet.append_row(list(new_user_data.values()))
        st.success("Registration successfull!")


# def login_user(username, password):
#     """Authenticate user by comparing entered password with stored hash."""
#     user = get_user_data(username)
#     if user and check_password_hash(user["password_hash"], password):
#         st.session_state["username"] = user["username"]
#         st.session_state["is_authenticated"] = True
#     else:
#         st.error("Wrong username or password.")
#         st.session_state["is_authenticated"] = False
#     st.rerun()


def apply_settings(username):
    try:
        # Loading data from Google Sheet
        users = sheet.get_all_records()
        # Looking for user by name
        for i, user in enumerate(users, start=2):  # Start with second row for data
            if user["username"] == username:
                st.session_state = json.loads(user["settings"])
                st.success("User settings applied successfully!")
    except:
        st.error("Can't apply user settings.")


def save_user_settings(username):
    try:
        settings_str = json.dumps(str(st.session_state))
        # Loading data from Google Sheet
        users = sheet.get_all_records()
        # Looking for user by name
        for i, user in enumerate(users, start=2):  # Start with second row for data
            if user["username"] == username:
                # Updating cell with user settings
                sheet.update_cell(i, sheet.find("settings").col, settings_str)
                st.success("User settings saved successfully!")
                return
    except:
        st.error("Can't save user settings.")


def load_user_settings(username):
    try:
        # Loading data from Google Sheet
        users = sheet.get_all_records()
        # Looking for user by name
        for i, user in enumerate(users, start=2):  # Start with second row for data
            if user["username"] == username:
                return json.loads(user["settings"])

    except:
        st.error("Can't display user settings.")


# Functions for import
# Func to save any user value except options
def save_user_cred(username, settings, settings_type):
    """Save user settings in Google Sheets."""
    users = sheet.get_all_records()
    for i, user in enumerate(users, start=2):
        if user["username"] == username:
            sheet.update_cell(i, sheet.find(settings_type).col, str(settings))
            st.success("Settings successfully saved!")
            break


# Streamlit UI
if "is_authenticated" not in st.session_state:
    st.session_state["is_authenticated"] = False

if st.session_state["is_authenticated"]:
    print(st.session_state)
    st.write(f"Welcome, {st.session_state["username"]}!")
    # Display settings
    settings_tuple = load_user_settings(st.session_state["username"])
    if settings_tuple:
        st.write("Your discount settings:", settings_tuple[0])
        st.write("Your wishlist settings:", settings_tuple[1])
    else:
        st.warning("No settings stored.")

    # Form to reset password
    with st.form("Password change form"):
        new_password = st.text_input("New password", type="password")
        new_password_confirmation = st.text_input("New password confirmation", type="password")
        if st.form_submit_button("Change password") and new_password == new_password_confirmation:
            save_user_cred(st.session_state["username"],
                           generate_password_hash(new_password), "password_hash")
            st.success("Password successfully saved.")

    if st.button("Log out"):
        st.session_state.clear()
        st.rerun()

else:
    print(st.session_state)
    with st.form("login_form"):
        st.write("Login Form")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Log in")

        # Login check
        if submit:
            if username and password:
                # login_user(username, password)
                apply_settings(username)
                user = get_user_data(username)
                if user and check_password_hash(user["password_hash"], password):
                    st.session_state["username"] = username
                    st.session_state["is_authenticated"] = True
                else:
                    st.error("Wrong username or password.")
                    st.session_state["is_authenticated"] = False
                st.rerun()
            else:
                st.error("You need to enter credentials")

    with st.form("registration_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        # Кнопка отправки внутри формы
        submitted = st.form_submit_button("Submit")

        # Логика при отправке формы
        if submitted:
            if password == confirm_password:
                st.success("User registered successfully")
                register_user(username, email, username, password)
            else:
                st.error("Passwords do not match.")

