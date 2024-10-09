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


def session_state_to_dict(session_state):
    # Convert SessionStateProxy object to a dictionary
    data = {}
    for key, value in session_state.items():
        # Handle different data types appropriately
        data[key] = value
    print(st.session_state)
    return {st.session_state["name"]: data}


# Custom deserialization function
def dict_to_session_state(data):
    # Convert dictionary back to a SessionStateProxy object
    session_state = st.session_state
    for key, value in data.items():
        # Set values in SessionStateProxy
        session_state[key] = value
    print(session_state)
    return session_state


# Pre-hashing all plain text passwords once
# stauth.Hasher.hash_passwords(config['credentials'])

# authenticator = stauth.Authenticate(
#     '../config.yaml'
# )

# Creating a login widget
try:
    st.session_state.authenticator.login()
    with open('config.yaml', 'r', encoding='utf-8') as file3:
        data = yaml.load(file3, Loader=SafeLoader)
    print(st.session_state.__str__())
    try:
        st.session_state = dict_to_session_state(data["credentials"][st.session_state["username"]])
    except:
        st.write("No user settings stored")
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
    if st.button("Save watcher settings"):
        settings = session_state_to_dict(st.session_state)
        with open('config.yaml', 'w', encoding='utf-8') as file2:
            yaml.dump(settings, file2, default_flow_style=False)
    if authenticator.logout():
        st.session_state.clear()
elif st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] is None:
    st.warning('Please enter your username and password')

# Saving config file
with open('config.yaml', 'w', encoding='utf-8') as file:
    yaml.dump(config, file, default_flow_style=False)
