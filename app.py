import streamlit as st


st.set_page_config(page_title="Steam Discount Watcher", page_icon=":material/troubleshoot:")

watcher_genre = st.Page("steamdiscountwatcher.py", title="Genre watcher", icon=":material/heap_snapshot_multiple:")
watcher_wishlist = st.Page("wishlistwatcher.py", title="Wishlist watcher", icon=":material/heap_snapshot_thumbnail:")
authentication = st.Page("user_settings.py", title="User settings", icon=":material/security_key:")

pg = st.navigation(
    {
        "Authorization": [authentication],
        "Services": [watcher_genre, watcher_wishlist]
    }
)
pg.run()