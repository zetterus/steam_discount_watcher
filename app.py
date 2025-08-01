import streamlit as st

# Настройка страницы
st.set_page_config(page_title="Steam Discount Watcher", page_icon=":material/troubleshoot:")

# Определение страниц без авторизации
watcher_genre = st.Page("steamdiscountwatcher.py", title="Genre watcher", icon=":material/heap_snapshot_multiple:")
watcher_wishlist = st.Page("wishlistwatcher.py", title="Wishlist watcher", icon=":material/heap_snapshot_thumbnail:")

# Настройка навигации
pg = st.navigation(
    {
        "Services": [watcher_genre, watcher_wishlist]
    }
)

pg.run()
