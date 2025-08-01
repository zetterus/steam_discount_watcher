# Import necessary modules
import time
import streamlit as st
import pandas as pd
import datetime as dt
from bs4 import BeautifulSoup
import requests
import json

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
    valid = True  # Flag to indicate valid input

    # Check if game_tag_id is an integer
    if not st.session_state.game_tag_id.isdigit():
        st.write("Error: Game tag ID must be an integer.")
        valid = False

    # Check if is_discounted is one of the new valid options
    valid_options = ("all", "with discount", "without discount")
    if st.session_state.is_discounted not in valid_options:
        st.write(f"Error: Discount option must be one of {valid_options}.")
        valid = False

    # If input is invalid, stop the execution
    if not valid:
        st.session_state.running = False

    return valid


# Main watcher function to collect data
def watcher():
    """
    Requests data from Steam and displays it in a DataFrame.
    """
    page_number = 0
    page_count = 100
    game_number = 1
    games_list = []

    # Loop while the watcher is running
    while True:
        # Check for page limit condition
        if st.session_state.limit_pages and page_number / page_count >= st.session_state.max_pages_input:
            print(f"Limit of {st.session_state.max_pages_input} pages reached. Search finished.")
            break

        # Determine the 'specials' parameter based on the user's choice.
        # specials=1 means games with discounts, specials=0 means all games.
        if st.session_state.is_discounted == "with discount":
            specials_param = "1"
        else:
            specials_param = "0"

        # Construct the URL for each page.
        url = f"https://store.steampowered.com/search/results/?query&start={page_number}&count={page_count}&dynamic_data=&sort_by=_ASC&tags={st.session_state.game_tag_id}&snr=1_7_7_2300_7&specials={specials_param}&infinite=1"

        # Send a request to the server
        response = requests.get(url)

        # Check the response
        if response.status_code == 200:
            # Parse the JSON response
            data = json.loads(response.text)

            # Extract HTML from "results_html" key
            results_html = data.get('results_html', '')

            # Parse HTML using BeautifulSoup
            soup = BeautifulSoup(results_html, 'html.parser')
            games_found = soup.find_all("a", class_="search_result_row")

            # --- DEBUGGING OUTPUT START ---
            print("---")
            print(f"Page {int(page_number / 100) + 1} requested.")
            print(f"Games found on this page: {len(games_found)}")
            # --- DEBUGGING OUTPUT END ---

            # If no games are found on the page, stop the search.
            if not games_found:
                print("No games found on this page. Search finished.")
                break

            # --- DEBUGGING OUTPUT CONTINUED ---
            print(f"First game: {games_found[0].find('span', class_='title').text}")
            print(f"Last game: {games_found[-1].find('span', class_='title').text}")
            print("---")
            # --- DEBUGGING OUTPUT END ---

            for game in games_found:
                game_name = game.find("span", class_="title").text
                game_link = game.get("href")

                discount_element = game.find("div", class_="discount_pct")

                # New and improved filtering logic for all three options.
                # It now checks for the presence of the discount element.
                if st.session_state.is_discounted == "with discount" and not discount_element:
                    continue  # Skip this game if we want discounts but no discount element is found

                if st.session_state.is_discounted == "without discount" and discount_element:
                    continue  # Skip this game if we want no discounts but a discount element is found

                # If the option is "all", or if the game matches the criteria for "with" or "without",
                # it will proceed.

                try:
                    # Get discount information if available
                    game_discount = discount_element.text
                    discount_original_price = game.find("div", class_="discount_original_price").text
                    discount_final_price = game.find("div", class_="discount_final_price").text
                    game_data = [game_number, game_name, game_discount, discount_final_price, discount_original_price,
                                 game_link]
                except AttributeError:
                    # This block will be executed for non-discounted games
                    game_data = [game_number, game_name, "N/A", "N/A", "N/A", game_link]

                game_number += 1
                games_list.append(game_data)

            # Move to the next page
            page_number += page_count
        else:
            st.write(f"Request error: {response.status_code}")
            break

    # Reset the running state after the watcher is done
    st.session_state.running = False

    # Print the last element of the list, as requested by the user
    if games_list:
        print(f"Final element: {games_list[-1]}")

    # Create a DataFrame
    df = pd.DataFrame(games_list,
                      columns=["#", "Game Name", "Discount", "Discounted Price", "Original Price", "Game Link"])

    # Change the index to start from 1
    df.index = range(1, len(df) + 1)

    # Display the DataFrame in Streamlit
    st.dataframe(df)


# DataFrame with genres
genres_df = pd.DataFrame({
    "Genre": ["Action", "Indie", "Adventure", "Casual", "RPG", "Strategy", "Simulation", "Early Access",
              "Free to Play", "Sports"],
    "Game ID": [19, 492, 21, 597, 122, 9, 599, 493, 113, 701]
})

# Split the interface into two columns
col1, col2 = st.columns(2)

# Second column for the genres table
col2.table(genres_df.set_index(genres_df.columns[0]))

# Initialize session state
if 'running' not in st.session_state:
    st.session_state.running = False
if 'game_tag_id' not in st.session_state:
    st.session_state.game_tag_id = "19"  # Default value for tag ID
if 'is_discounted' not in st.session_state:
    st.session_state.is_discounted = "all"  # Default value is now "all"
if 'is_discounted_index' not in st.session_state:
    st.session_state.is_discounted_index = 0
# Add new session state for page limit
if 'limit_pages' not in st.session_state:
    st.session_state.limit_pages = False
# Initialize the variable for the input field with a key
if 'max_pages_input' not in st.session_state:
    st.session_state.max_pages_input = 10

# First column for app control
if st.session_state.running:
    col1.write("<h4>Watcher is running</h4>", unsafe_allow_html=True)
    # The watcher is now called without a loop inside
    watcher()
    if col1.button("Reset Watcher"):
        st.session_state.running = False
        st.rerun()
else:
    col1.write("<h4>Watcher is not running</h4>", unsafe_allow_html=True)

    # Input fields for the user
    st.session_state.game_tag_id = col1.text_input("Enter Game Tag ID:", value=st.session_state.game_tag_id)

    # New options for the radio button
    is_discounted_option = col1.radio("Search games:", options=("all", "with discount", "without discount"),
                                      index=st.session_state.is_discounted_index)

    # Update session state based on the selected option
    st.session_state.is_discounted = is_discounted_option
    if is_discounted_option == "all":
        st.session_state.is_discounted_index = 0
    elif is_discounted_option == "with discount":
        st.session_state.is_discounted_index = 1
    else:
        st.session_state.is_discounted_index = 2

    # New controls for page limit
    st.session_state.limit_pages = col1.checkbox("Limit number of pages?", value=st.session_state.limit_pages)
    if st.session_state.limit_pages:
        # Now using a key for the input field to allow Streamlit to automatically manage the state
        col1.number_input("Number of pages (max 100):", min_value=1, max_value=100, value=10, key='max_pages_input')

    with col1:
        # Button to run
        if st.button("Run Watcher Now"):
            if query_check():
                st.session_state.running = True
                col2.markdown("---")
                col2.write("Watcher successfully started.")
                time.sleep(1)
                st.rerun()
            else:
                st.write("Error: Invalid input. Watcher not started.")
