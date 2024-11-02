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
@st.cache_data
def get_user_data(username):
    """Fetch user data from Google Sheets by username."""
    users = sheet.get_all_records()
    for user in users:
        if user['username'] == username:
            return user
    return None


@st.cache_data
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
            "settings": json.dumps(
                {"game_tag_id": "", "is_discounted_index": 0, "selected_days_g": None,
                 "scheduled_time_g": "12:00", "user_id": "", "game_tag": "",
                 "selected_days_w": None, "scheduled_time_w": "12:00"}),
        }
        sheet.append_row(list(new_user_data.values()))
        st.success("Registered successfully.")


# @st.cache_data
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

@st.cache_data
def apply_settings(username):
    try:
        # Loading data from Google Sheet
        users = sheet.get_all_records()
        # Looking for user by name
        for i, user in enumerate(users, start=2):  # Start with second row for data
            if user["username"] == username:
                for key, value in json.loads(user["settings"]).items():
                    if key in ("scheduled_time_g", "scheduled_time_w"):
                        st.session_state[key] = dt.datetime.strptime(value, "%H:%M")
                    else:
                        st.session_state[key] = value
        print("applying success")
    except:
        st.error("Can't apply user settings.")


@st.cache_data
def save_user_settings(username):
    def custom_encoder(obj):
        if isinstance(obj, dt.datetime):
            return obj.isoformat()  # Преобразуем время в строку
        raise TypeError(f"Type {type(obj)} is not JSON serializable")
    # Преобразуем st.session_state в JSON-строку
    st_state_json = json.dumps(st.session_state, default=custom_encoder, indent=2)
    try:
        # Loading data from Google Sheet
        users = sheet.get_all_records()
        # Looking for user by name
        for i, user in enumerate(users, start=2):  # Start with second row for data
            if user["username"] == username:
                # Updating cell with user settings
                sheet.update_cell(i, sheet.find("settings").col, st_state_json)
                st.success("User settings saved successfully!")
    except:
        st.error("Can't save user settings.")


@st.cache_data
def load_user_settings(username):
    # try:
    # Loading data from Google Sheet
    users = sheet.get_all_records()
    # Looking for user by name
    for i, user in enumerate(users, start=2):  # Start with second row for data
        if user["username"] == username:
            loa = json.loads(user["settings"])
            print(loa)
            print(type(loa))
            return loa

    # except:
    #     st.error("Can't load user settings.")


# Functions for import
# Func to save any user value except options
@st.cache_data
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
    st.write(f"Welcome, {st.session_state["username"]}!")
    # Display settings
    settings_tuple = load_user_settings(st.session_state["username"])
    if settings_tuple:
        st.write("Your discount settings:", settings_tuple)
        # st.write("Your wishlist settings:", settings_tuple[1])
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
    with st.form("login_form", clear_on_submit=True):
        st.write("Login Form")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Log in")

        # Login check
        if submit:
            if username and password:
                user = get_user_data(username)
                if user:
                    # login_user(username, password)
                    apply_settings(username)
                    if user and check_password_hash(user["password_hash"], password):
                        st.session_state["username"] = username
                        st.session_state["is_authenticated"] = True
                    else:
                        st.error("Wrong username or password.")
                        st.session_state["is_authenticated"] = False
                    st.rerun()
                else:
                    st.error("No user found.")
            else:
                st.error("You need to enter credentials")

    with st.form("registration_form", clear_on_submit=True):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        # Кнопка отправки внутри формы
        submitted = st.form_submit_button("Submit")

        # Логика при отправке формы
        if submitted:
            if password == confirm_password:
                register_user(username, email, username, password)
            else:
                st.error("Passwords do not match.")
