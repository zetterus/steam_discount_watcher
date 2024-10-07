import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

st.set_page_config(page_title="Steam Discount Watcher", page_icon=":material/troubleshoot:")

watcher_genre = st.Page("steamdiscountwatcher.py", title="Genre watcher", icon=":material/heap_snapshot_multiple:")
watcher_wishlist = st.Page("wishlistwatcher.py", title="Wishlist watcher", icon=":material/heap_snapshot_thumbnail:")

authentication = st.Page("user_settings.py", title="User settings", icon=":material/security_key:")
registration = st.Page("registration.py", title="Registration", icon=":material/how_to_reg:")

pg = st.navigation(
    {
        "Services": [watcher_genre, watcher_wishlist],
        "Authorization": [authentication, registration]
    }
)
pg.run()

# Loading config file
with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)
    st.session_state.config = config

# Creating the authenticator object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)
st.session_state.authenticator = authenticator
