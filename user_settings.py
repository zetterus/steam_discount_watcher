import yaml
import streamlit as st
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import datetime as dt
from streamlit_authenticator.utilities import (CredentialsError,
                                               ForgotError,
                                               Hasher,
                                               LoginError,
                                               RegisterError,
                                               ResetError,
                                               UpdateError)

# Loading config file
with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Creating the authenticator object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)


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


def save_user_settings(current_filename):
    # loading data from YAML-file
    with open('config.yaml', 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)

    username = st.session_state["username"]  # current user

    # check from which file function runs
    if current_filename == "steamdiscountwatcher.py":
        user_settings = {
            "game_tag_id": st.session_state.game_tag_id,
            "is_discounted_index": st.session_state.is_discounted_index,
            "selected_days_cron": st.session_state.selected_days_cron,
            "scheduled_time": st.session_state.scheduled_time.strftime("%H:%M")  # converting time to string
        }
        data["credentials"]["usernames"][username]["settings_discount"] = user_settings
    elif current_filename == "wishlistwatcher.py":
        user_settings = {
            "user_id": st.session_state.user_id,
            "game_tag": st.session_state.game_tag,
            "selected_days_cron": st.session_state.selected_days_cron,
            "scheduled_time": st.session_state.scheduled_time.strftime("%H:%M")  # converting time to string
        }
        data["credentials"]["usernames"][username]["settings_wishlist"] = user_settings
    else:
        st.write("Error: Unknown source file.")

    # saving updated options to YAML-file
    with open('config.yaml', 'w', encoding='utf-8') as file:
        yaml.dump(data, file, default_flow_style=False)

    st.write("Settings saved successfully!")


def load_user_settings(current_filename):
    with open('config.yaml', 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)

    username = st.session_state["username"]

    if current_filename == "steamdiscountwatcher.py":
        user_settings = data["credentials"]["usernames"][username].get("settings_discount", {})
    elif current_filename == "wishlistwatcher.py":
        user_settings = data["credentials"]["usernames"][username].get("settings_wishlist", {})
    else:
        st.write("Error: Unknown source file.")
        user_settings = {}

    return user_settings


def apply_settings_to_widgets(user_settings, current_filename):
    if user_settings:
        if current_filename == "steamdiscountwatcher.py":
            st.session_state["game_tag_id"] = user_settings.get("game_tag_id", "")
            st.session_state["is_discounted_index"] = user_settings.get("is_discounted_index", 0)
            st.session_state["selected_days_cron"] = user_settings.get("selected_days_cron", [])
            st.session_state["scheduled_time"] = dt.datetime.strptime(user_settings.get("scheduled_time", "12:00"),
                                                                      "%H:%M").time()
        elif current_filename == "wishlistwatcher.py":
            st.session_state["user_id"] = user_settings.get("user_id", "")
            st.session_state["game_tag"] = user_settings.get("game_tag", "")
            st.session_state["selected_days_cron"] = user_settings.get("selected_days_cron", [])
            st.session_state["scheduled_time"] = dt.datetime.strptime(user_settings.get("scheduled_time", "12:00"),
                                                                      "%H:%M").time()
        else:
            st.write("Error: can't apply settings.")
    else:
        st.write("No settings found for the user.")


# Creating a login widget
try:
    authenticator.login()
    with open('config.yaml', 'r', encoding='utf-8') as file3:
        data = yaml.load(file3, Loader=SafeLoader)
    with open('config.yaml', 'w', encoding='utf-8') as file3:
        yaml.dump(data, file3, default_flow_style=False)
    with open('config.yaml', 'r', encoding='utf-8') as file3:
        data = yaml.load(file3, Loader=SafeLoader)
    try:
        st.session_state = dict_to_session_state(data)
    except:
        st.write("Can't load user settings")
except Exception as e:
    st.write(e)

# Authenticating user
if st.session_state['authentication_status']:
    st.write(f'Welcome **{st.session_state["name"]}**')

    if authenticator.logout():
        st.session_state.clear()
        st.rerun()

    try:
        st.write("Your genre watcher settings",
                 data["credentials"]["usernames"][st.session_state['username']]["settings_discount"])
    except:
        st.write("No genre watcher settings stored")
    try:
        st.write("Your wishlist watcher settings",
                 data["credentials"]["usernames"][st.session_state['username']]["settings_wishlist"])
    except:
        st.write("No wishlist watcher settings stored")


elif st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] is None:
    st.warning('Please enter your username and password')

# Creating a password reset widget
if st.session_state['authentication_status']:
    try:
        if authenticator.reset_password(st.session_state['username']):
            st.success('Password modified successfully')
    except (CredentialsError, ResetError) as e:
        st.error(e)

# Creating a new user registration widget
if not st.session_state['authentication_status']:
    try:
        (email_of_registered_user,
         username_of_registered_user,
         name_of_registered_user) = authenticator.register_user(captcha=False, clear_on_submit=True)
        if email_of_registered_user:
            st.success('User registered successfully')
    except RegisterError as e:
        st.error(e)


with open('config.yaml', 'w') as file:
    yaml.dump(config, file, default_flow_style=False)

