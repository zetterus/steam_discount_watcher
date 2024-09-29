import streamlit as st

st.set_page_config(page_title="Steam Discount Watcher", page_icon=":material/troubleshoot:")

watcher_genre = st.Page("steamdiscountwatcher.py", title="Genre watcher", icon=":material/heap_snapshot_multiple:")
watcher_wishlist = st.Page("wishlistwatcher.py", title="Wishlist watcher", icon=":material/heap_snapshot_thumbnail:")

test = st.Page("test.py", title="test", icon=":material/heap_snapshot_thumbnail:")

pg = st.navigation(
    {
    "Services": [watcher_genre, watcher_wishlist],
        "Authorization": [test]
    }
)
pg.run()

