"""
Script description: This script imports tests the Streamlit-Authenticator package.

Libraries imported:
- yaml: Module implementing the data serialization used for human readable documents.
- streamlit: Framework used to build pure Python web applications.
"""

import yaml
import streamlit as st
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import (CredentialsError,
                                               ForgotError,
                                               Hasher,
                                               LoginError,
                                               RegisterError,
                                               ResetError,
                                               UpdateError)

# Pre-hashing all plain text passwords once
# stauth.Hasher.hash_passwords(config['credentials'])

# authenticator = stauth.Authenticate(
#     '../config.yaml'
# )

# Creating a login widget
try:
    st.session_state.authenticator.login()
except LoginError as e:
    st.error(e)

# # Creating a guest login button
# try:
#     authenticator.experimental_guest_login('Login with Google', provider='google',
#                                             oauth2=config['oauth2'])
#     authenticator.experimental_guest_login('Login with Microsoft', provider='microsoft',
#                                             oauth2=config['oauth2'])
# except LoginError as e:
#     st.error(e)
# unable to github secret store politics?

# Authenticating user
config = st.session_state.config
authenticator = st.session_state.authenticator
if st.session_state['authentication_status']:
    st.write(f'Welcome *{st.session_state["name"]}*')
    save_btn = st.button("Save watcher settings")
    if save_btn:
        user_settings = {config["name"]: st.session_state.game_tag_id,
                         st.session_state.is_discounted, st.session_state.selected_days_cron, st.session_state.scheduled_time}
        with open('user_settings.py', 'w', encoding='utf-8') as file2:
            yaml.dump(user_settings, file2, default_flow_style=False)
    authenticator.logout()
elif st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] is None:
    st.warning('Please enter your username and password')

# Saving config file
with open('config.yaml', 'w', encoding='utf-8') as file:
    yaml.dump(config, file, default_flow_style=False)
