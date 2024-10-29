import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Pre-hashing all plain text passwords once
# stauth.Hasher.hash_passwords(config['credentials'])

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

try:
    email_of_registered_user, username_of_registered_user, \
    name_of_registered_user = authenticator.register_user(captcha=False, clear_on_submit=True)
    if email_of_registered_user:
        st.success('User registered successfully')
    st.write(authenticator.attrs)
    st.write(authenticator.__dict__)
    st.write(authenticator.__str__())
    st.write(authenticator.authentication_controller)
    st.write(authenticator.__repr__())
    st.write(authenticator.__dir__())
except Exception as e:
    st.error(e)
