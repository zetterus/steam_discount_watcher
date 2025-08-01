# Import necessary modules
import streamlit as st
import pandas as pd
import requests
import json
import time

# Remove Streamlit UI elements like the hamburger button
st.markdown("""
<style>
.st-emotion-cache-yfhhig.ef3psqc5
{
visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# Function to check user input validity
def query_check():
    """
    Checks the validity of user input and returns True or False.
    """
    valid = True

    # Check if user_id is a digit
    if not st.session_state.user_id.isdigit():
        st.write("Error: User ID must be an integer.")
        valid = False

    # Check if the selected game tag is valid
    if st.session_state.game_tag.capitalize() not in (
            "Action", "Indie", "Adventure", "Casual", "RPG", "Strategy", "Simulation", "Early Access", "Free to Play",
            "Sports", "All"):
        st.write("Error: Invalid game tag.")
        valid = False

    # If input is invalid, stop the execution
    if not valid:
        st.session_state.running = False

    return valid


# Main watcher function for the wishlist
def personal_watcher():
    """
    Watches the user's wishlist and displays results in a DataFrame.
    """
    page = 0
    game_number = 1
    columns = ["Game Name", "Discount", "Discounted Price", "Game Tags", "Game Link"]
    games_list = []

    # Loop to fetch wishlist pages
    while st.session_state.running:
        url = F"https://store.steampowered.com/wishlist/profiles/{st.session_state.user_id}/wishlistdata/?p={page}&v="

        response = requests.get(url)

        if response.status_code == 200:

            # First, check if the response content type is JSON.
            # This is a more robust way to handle cases where Steam returns an HTML page.
            if 'application/json' not in response.headers.get('Content-Type', ''):
                st.write("Error: The Steam profile page returned an HTML response instead of JSON data. "
                         "This often happens if the SteamID64 is incorrect or the wishlist is private. "
                         "Please check your ID and make sure your wishlist is set to public.")
                st.session_state.running = False
                break

            try:
                # Attempt to load JSON data from the response
                games_data = json.loads(response.text)
            except json.JSONDecodeError:
                # Handle cases where the response is not valid JSON
                st.write(
                    "Error: Could not retrieve data. Please check if the SteamID64 is correct and your wishlist is public.")
                st.session_state.running = False
                break

            # If no games are found on the page, stop the search
            if not games_data:
                st.write("Search finished.")
                break

            for game_id, game_info in games_data.items():
                game_name = game_info.get("name")
                game_tags = game_info.get("tags")

                # Check if the game matches the selected genre
                if st.session_state.game_tag.capitalize() in game_tags or st.session_state.game_tag == "All":
                    # Get discount information
                    try:
                        discount_pct = game_info["subs"][0].get("discount_pct")
                        price_formatted = f"{(game_info['subs'][0]['price'] / 100):.2f}"
                    except (KeyError, IndexError):
                        # Handle cases where there's no discount or price info
                        discount_pct = "N/A"
                        price_formatted = "N/A"

                    # Filtering logic is now only for genre.
                    game_data = [game_name, discount_pct, price_formatted, ", ".join(game_tags),
                                 F"https://store.steampowered.com/app/{game_id}"]
                    games_list.append(game_data)
                    game_number += 1

            page += 1
        else:
            st.write(f"Request error: {response.status_code}")
            st.session_state.running = False
            break

    # Reset the running state after the watcher is done
    st.session_state.running = False

    # Create DataFrame from the list of games
    df = pd.DataFrame(games_list, columns=columns)
    df.index = range(1, len(df) + 1)
    st.dataframe(df)


# List of genres
genres = ["All", "Action", "Indie", "Adventure", "Casual", "RPG", "Strategy", "Simulation", "Early Access",
          "Free to Play", "Sports"]
genres_df = pd.DataFrame({'Genre': genres}, index=list(range(1, len(genres) + 1)))

# Initialize session state
if 'running' not in st.session_state:
    st.session_state.running = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = ""
if 'game_tag' not in st.session_state:
    st.session_state.game_tag = "All"  # Default value is now "All"

# Split the UI into two columns
col1, col2 = st.columns(2)
col2.table(genres_df)

if st.session_state.running:
    col1.write("<h4>Watcher is running</h4>", unsafe_allow_html=True)
    personal_watcher()
    if col1.button("Reset Watcher"):
        st.session_state.running = False
        st.rerun()
else:
    col1.write("<h4>Watcher is not running</h4>", unsafe_allow_html=True)
    st.session_state.user_id = col1.text_input("Enter SteamID64:", value=st.session_state.user_id)

    # Use a selectbox for genres to prevent typos
    st.session_state.game_tag = col1.selectbox("Select game genre:", options=genres,
                                               index=genres.index(st.session_state.game_tag))

    with col1:
        if st.button("Run Watcher Now"):
            if query_check():
                st.session_state.running = True
                col2.markdown("---")
                col2.write("Watcher successfully started.")
                time.sleep(1)
                st.rerun()
            else:
                st.write("Error: Invalid input. Watcher not started.")
