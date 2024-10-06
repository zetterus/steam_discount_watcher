import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Pre-hashing all plain text passwords once
stauth.Hasher.hash_passwords(config['credentials'])

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    auto_hash=False
)

# login widget
try:
    authenticator.login(clear_on_submit=True, key="Login")
except Exception as e:
    st.error(e)

# authenticating users and logout button
if st.session_state['authentication_status']:
    authenticator.logout()
    st.write(f'Welcome *{st.session_state["name"]}*')
    st.title('Some content')
elif st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] is None:
    st.warning('Please enter your username and password')

# reset password widget
if st.session_state['authentication_status']:
    try:
        if authenticator.reset_password(st.session_state['username']):
            st.success('Password modified successfully')
    except Exception as e:
        st.error(e)

# new user registration widget
try:
    email_of_registered_user, \
    username_of_registered_user, \
    name_of_registered_user = authenticator.register_user(pre_authorized=config['pre-authorized'])
    if email_of_registered_user:
        st.success('User registered successfully')
except Exception as e:
    st.error(e)
