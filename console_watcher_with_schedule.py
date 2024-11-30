import requests
import json
import schedule
import time

while True:
    try:
        user_id = input("Enter user steam SteamID64:")  # 76561198120742945
        user_id == int(user_id)
        game_tag = input(
            "Action|Indie|Adventure|Casual|RPG|Strategy|Simulation|Early Access|Free to Play|Sports|All\nEnter game tag:")
        game_tag == str(game_tag)
        scheduled_time = input("Input check time(example 14:30):")
        0 < int(scheduled_time.split(":")[0]) < 24
        0 < int(scheduled_time.split(":")[1]) < 60
        print("Input accepted")
        break
    except:
        print("Invalid user.. input")


def personal_watcher():
    page = 0

    # Открываем файл в режиме записи, чтобы очистить его
    with open("watcher_report.txt", "w", encoding="utf-8") as file:
        pass

    # Открываем файл в режиме добавления
    with open("watcher_report.txt", "a", encoding="utf-8") as file:
        while True:
            url = F"https://store.steampowered.com/wishlist/profiles/{user_id}/wishlistdata/?p={page}&v="
            response = requests.get(url)
            games_data = json.loads(response.text)

            if games_data:
                for game_id, game_info in games_data.items():
                    game_name = game_info.get("name")
                    game_price = game_info["subs"][0].get("price") if game_info.get("subs") else "N/A"
                    game_discount = game_info["subs"][0].get("discount_pct") if game_info.get("subs") else "N/A"
                    game_tags = game_info.get("tags")
                    try:
                        if game_tag in game_tags or game_tag == "All":
                            file.write(
                                F"{game_id}|{game_name}|{game_price}|{game_discount}|{game_tags}\nhttps://store.steampowered.com/app/{game_id}\n")

                    except:
                        print(game_name, "write error")
                print(F"Page {page} processed.")
                page += 1
            else:
                print(F"End of request.")
                break


schedule.every().day.at(scheduled_time).do(personal_watcher)

while True:
    schedule.run_pending()
    time.sleep(60)
