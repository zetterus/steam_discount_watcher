import time
import os
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
        st.warning("Пользователь с таким именем уже существует.")
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
        st.success("Пользователь успешно зарегистрирован!")


def login_user(username, password):
    """Authenticate user by comparing entered password with stored hash."""
    user = get_user_data(username)
    if user and check_password_hash(user["password_hash"], password):
        st.session_state["user"] = user
        st.session_state["is_authenticated"] = True
    else:
        st.error("Неправильное имя пользователя или пароль.")
        st.session_state["is_authenticated"] = False
    st.rerun()


def logout_user(username, current_filename):
    user_settings = load_user_settings(username, current_filename)
    for key in list(user_settings.keys()):
        del st.session_state[key]
    st.session_state["user"] = None
    st.session_state["is_authenticated"] = False
    st.success("You successfully log out.")
    time.sleep(3)
    st.rerun()  # Перезагружает страницу, чтобы отобразить пустое состояние


def apply_settings(username, current_filename):
    user_settings = load_user_settings(username, current_filename)

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


# Functions for import
def save_user_settings(username, settings, settings_type):
    """Save user settings in Google Sheets."""
    users = sheet.get_all_records()
    for i, user in enumerate(users, start=2):
        if user["username"] == username:
            current_settings = json.loads(user[settings_type])
            current_settings.update(settings)
            sheet.update_cell(i, sheet.find(settings_type).col, json.dumps(current_settings))
            st.success("Настройки успешно сохранены!")
            break


def load_user_settings(username, settings_type):
    """Load user settings from Google Sheets."""
    user = get_user_data(username)
    if user:
        return json.loads(user[settings_type])
    return {}


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


# Streamlit UI
if "is_authenticated" not in st.session_state:
    st.session_state["is_authenticated"] = False

if st.session_state["is_authenticated"]:
    st.write(f"Добро пожаловать, {st.session_state['user']['name']}!")

    # Display settings
    discount_settings = load_user_settings(st.session_state["user"]["username"], "wishlistwatcher.py")
    wishlist_settings = load_user_settings(st.session_state["user"]["username"], "steamdiscountwatcher.py")
    st.write("Ваши настройки скидок:", discount_settings)
    st.write("Ваши настройки списка желаемого:", wishlist_settings)

    # Form to reset password
    new_password = st.text_input("Новый пароль", type="password")
    if st.button("Сменить пароль"):
        save_user_settings(st.session_state["user"]["username"],
                           {"password_hash": generate_password_hash(new_password)}, "password_hash")
        st.success("Пароль успешно обновлен.")

    if st.button("Log out"):
        time.sleep(3)
        logout_user(st.session_state["user"]["username"], os.path.basename(__file__))

else:
    with st.form("login_form"):
        st.write("Войдите в аккаунт или зарегистрируйтесь")
        username = st.text_input("Имя пользователя", key="username")
        password = st.text_input("Пароль", key="password", type="password")

        if st.form_submit_button("Log in"):
            if username and password:
                login_user(username, password)
                load_settings(username, os.path.basename(__file__))
            else:
                st.error("You need to enter credentials")

    with st.form("registration_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        # Кнопка отправки внутри формы
        submitted = st.form_submit_button("Зарегистрироваться")

        # Логика при отправке формы
        if submitted:
            if password == confirm_password:
                st.success("User registered successfully")
                register_user(username, email, username, password)
            else:
                st.error("Passwords do not match.")
