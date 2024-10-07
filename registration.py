import yaml
import streamlit as st
from yaml.loader import SafeLoader
from streamlit_authenticator.utilities import (CredentialsError,
                                               ForgotError,
                                               Hasher,
                                               LoginError,
                                               RegisterError,
                                               ResetError,
                                               UpdateError)

# Authenticating user check
if st.session_state['authentication_status']:
    st.write(f'Welcome *{st.session_state["name"]}*')
elif st.session_state['authentication_status'] is False:
    st.error('You need to login')
elif st.session_state['authentication_status'] is None:
    st.warning('You need to login')

# Creating a password reset widget
if st.session_state['authentication_status']:
    try:
        if st.session_state.authenticator.reset_password(st.session_state['username']):
            st.success('Password modified successfully')
    except (CredentialsError, ResetError) as e:
        st.error(e)

# Creating a new user registration widget
try:
    (email_of_registered_user,
     username_of_registered_user,
     name_of_registered_user) = st.session_state.authenticator.register_user(captcha=False, clear_on_submit=True)
    if email_of_registered_user:
        st.success('User registered successfully')
except RegisterError as e:
    st.error(e)

# Creating a forgot password widget
try:
    (username_of_forgotten_password,
     email_of_forgotten_password,
     new_random_password) = st.session_state.authenticator.forgot_password(clear_on_submit=True)
    if username_of_forgotten_password:
        st.success('New password sent securely')
        # Random password to be transferred to the user securely
    elif not username_of_forgotten_password:
        st.error('Username not found')
except ForgotError as e:
    st.error(e)

# Creating a forgot username widget
try:
    (username_of_forgotten_username,
     email_of_forgotten_username) = st.session_state.authenticator.forgot_username(clear_on_submit=True)
    if username_of_forgotten_username:
        st.success('Username sent securely')
        # Username to be transferred to the user securely
    elif not username_of_forgotten_username:
        st.error('Email not found')
except ForgotError as e:
    st.error(e)

# Creating an update user details widget
if st.session_state['authentication_status']:
    try:
        if st.session_state.authenticator.update_user_details(st.session_state['username']):
            st.success('Entry updated successfully')
    except UpdateError as e:
        st.error(e)

# Saving config file
config = st.session_state.config
with open('config.yaml', 'w', encoding='utf-8') as file:
    yaml.dump(config, file, default_flow_style=False)
