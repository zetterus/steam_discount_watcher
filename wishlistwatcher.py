import streamlit as st
import pandas as pd
import requests
import json
import schedule
import time

# remove streamlit hamburger (& any other elements)
st.markdown("""
<style>
.st-emotion-cache-yfhhig.ef3psqc5
{
visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# # completely removes header
# .st-emotion-cache-h4xjwg.ezrtsby2
# {
# visibility: hidden;
# }

def query_check():
    valid = True

    try:
        st.session_state.user_id = int(st.session_state.user_id)
    except ValueError:
        st.write("Error: user id must be an integer.")
        valid = False

    if st.session_state.game_tag not in (
            "Action", "Indie", "Adventure", "Casual", "RPG", "Strategy", "Simulation", "Early Access", "Free to Play",
            "Sports", "All"):
        st.write("Error: invalid game tag.")
        valid = False

    try:
        0 < int(st.session_state.scheduled_time.split(":")[0]) < 24
        0 < int(st.session_state.scheduled_time.split(":")[1]) < 60
    except ValueError:
        st.write("Error: user id must be an integer.")
        valid = False

    if valid:
        # st.session_state.running = True
        st.write("Query seems valid!")
    else:
        st.write("Please fix the errors mentioned above.")
        # st.session_state.running = False
        time.sleep(5)
        st.rerun()

    # while True:
    #     try:
    #         st.session_state.user_id = input("Enter user steam SteamID64:")  # 76561198120742945
    #         st.session_state.user_id == int(st.session_state.user_id)
    #         st.session_state.game_tag = input(
    #             "Action|Indie|Adventure|Casual|RPG|Strategy|Simulation|Early Access|Free to Play|Sports|All\nEnter game tag:")
    #         st.session_state.game_tag == str(st.session_state.game_tag)
    #         st.session_state.scheduled_time = input("Input check time(example 14:30):")
    #         0 < int(st.session_state.scheduled_time.split(":")[0]) < 24
    #         0 < int(st.session_state.scheduled_time.split(":")[1]) < 60
    #         st.write("Input accepted")
    #         break
    #     except:
    #         st.write("Invalid user.. input")


def personal_watcher():
    # Starting page number
    page = 0
    game_number = 1

    # dataframe headers
    columns = ["№", "Game Name", "Discount", "Discounted Price", "Game Tags", "Game Link"]

    # games list initialization
    games_list = []

    # adding games to list
    while True:
        # formating url for each page
        url = F"https://store.steampowered.com/wishlist/profiles/{st.session_state.user_id}/wishlistdata/?p={page}&v="

        # sending query to server
        response = requests.get(url)

        # response check
        if response.status_code == 200:

            games_data = json.loads(response.text)

            for game_id, game_info in games_data.items():
                game_name = game_info.get("name")
                game_price = game_info["subs"][0].get("price") if game_info.get("subs") else "N/A"
                game_discount = game_info["subs"][0].get("discount_pct") if game_info.get("subs") else "N/A"
                game_tags = game_info.get("tags")
                try:
                    if st.session_state.game_tag in game_tags or st.session_state.game_tag == "All":
                        if game_discount:
                            game_data = [game_number, game_name, game_discount, game_price, game_tags,
                                         F"https://store.steampowered.com/app/{game_id}"]
                except:
                    print(game_name, "write error")

                games_list.append(game_data)
                game_number += 1

            print(F"Page {page} processed.")  # TODO: убрать
            page += 1

        else:
            st.write(f"Query error: {response.status_code}")
            break

    # creating dataframe
    df = pd.DataFrame(games_list,
                      columns=["№", "Game Name", "Discount", "Discounted Price", "Original Price", "Game Link"])

    # changing index to start from 1
    df.index = range(1, len(df) + 1)

    # display DataFrame in Streamlit
    st.dataframe(df)

    st.session_state.task_done = True


schedule.every().day.at(st.session_state.scheduled_time).do(personal_watcher)

while True:
    schedule.run_pending()
    time.sleep(60)
