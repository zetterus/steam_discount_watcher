import streamlit as st
import pandas as pd
import datetime as dt
from bs4 import BeautifulSoup
import requests
import json
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()


# #remove streamlit hamburger (& any other elements)
# st.markdown("""
# <style>
# .st-emotion-cache-yfhhig.ef3psqc5
# {
# visibility: hidden;
# }
# </style>
# """, unsafe_allow_html=True)
# # completely removes header
# .st-emotion-cache-h4xjwg.ezrtsby2
# {
# visibility: hidden;
# }

# query check
def query_check():
    """
    This function checks the validity of user input and displays messages accordingly.
    """
    global game_tag_id, is_discounted, scheduled_time  # Access global variables

    valid = True  # Flag to indicate valid input

    # Check game_tag_id is an integer
    try:
        game_tag_id = int(game_tag_id)
    except ValueError:
        st.write("Error: game tag id must be an integer.")
        valid = False

    # Check is_discounted is either "yes" or "no"
    if is_discounted not in ("yes", "no"):
        st.write("Error: discount option must be 'yes' or 'no'.")
        valid = False

    # Check scheduled_time is a valid time object
    if not isinstance(scheduled_time, dt.time):
        st.write("Error: invalid time format. Please use the time picker.")
        valid = False

    if valid:
        st.session_state.running = True
        st.write("Query seems valid!")
    else:
        st.write("Please fix the errors mentioned above.")
        # You can optionally clear the input fields here for a better user experience.


# run watcher through planner function
def start_watcher():
    global scheduled_time, selected_days
    scheduler.add_job(
        watcher,
        'cron',
        hour=scheduled_time.hour,
        minute=scheduled_time.minute,
        day_of_week=','.join(selected_days_cron)  # Формат: 'mon,tue,wed'
    )
    scheduler.start()


def watcher():  # нужно сделать запись результатов не в файл а в таблицу
    # Начальный номер страницы
    page_number = 0
    page_count = 100  # Количество игр на одной странице, больше 100 не даёт?
    game_number = 1

    # заголовки датафрейма
    columns = ["№", "Game Name", "Discount", "Discounted Price", "Original Price", "Game Link"]

    # создаём словарь с играми
    games_list = []

    # добавляем игры в словарь
    while True:
        # Формируем URL для каждой страницы
        url = f"https://store.steampowered.com/search/results/?query&start={page_number}&count={page_count}&dynamic_data=&sort_by=_ASC&tags={game_tag_id}&snr=1_7_7_2300_7&specials={is_discounted}&infinite=1"

        # Отправляем запрос на сервер
        response = requests.get(url)

        # Проверяем статус ответа
        if response.status_code == 200:
            # Парсим JSON ответ
            data = json.loads(response.text)

            # Извлекаем HTML из ключа "results_html"
            results_html = data.get('results_html', '')

            # Если результатов нет, завершаем цикл
            if results_html == "\r\n<!-- List Items -->\r\n<!-- End List Items -->\r\n":
                print("Search end")
                break

            # Парсим HTML с помощью BeautifulSoup
            soup = BeautifulSoup(results_html, 'html.parser')
            games_found = soup.find_all("a", class_="search_result_row")

            for game in games_found:
                game_name = game.find("span", class_="title").text
                game_link = game.get("href")
                try:
                    game_discount = game.find("div", class_="discount_pct").text
                    discount_original_price = game.find("div", class_="discount_original_price").text
                    discount_final_price = game.find("div", class_="discount_final_price").text
                    game_data = [game_number, game_name, game_discount, discount_final_price, discount_original_price,
                                 game_link]
                except:
                    game_data = [game_number, game_name, "N/A", "N/A", "N/A", game_link]

                game_number += 1
                games_list.append(game_data)

            # Переходим к следующей странице
            print(F"page {page_number} proceeded")
            page_number += page_count
        else:
            st.write(f"Query error: {response.status_code}")
            break

    # Создаем DataFrame
    st.write("creating dataframe")
    df = pd.DataFrame(games_list,
                      columns=["№", "Game Name", "Discount", "Discounted Price", "Original Price", "Game Link"])

    # Изменяем индекс, чтобы начинался с 1
    df.index = range(1, len(df) + 1)

    # Отображаем DataFrame в Streamlit
    st.write("writing dataframe")
    st.dataframe(df)


st.markdown("<h4 style='text-align: center;'>WARNING! Frequent usage may cause block. Use at your own risk.</h4>",
            unsafe_allow_html=True)
st.markdown("---")

genres_df = pd.DataFrame({
    "genres": ["Action", "Indie", "Adventure", "Casual", "RPG", "Strategy", "Simulation", "Early Access",
               "Free to Play", "Sports"],
    "game_id": [19, 492, 21, 597, 122, 9, 599, 493, 113, 701]
})

# columns
col1, col2 = st.columns(2)

# app status checkup
if 'running' not in st.session_state:
    st.session_state.running = False
    submit_btn_status, run_btn_status = False, False
else:
    submit_btn_status, run_btn_status = False, False

# 1st column
# genres ids
col1.table(genres_df.set_index(genres_df.columns[0]))
days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
selected_days = col1.multiselect("Select the days of the week:", days_of_week, default=['Monday'])
day_mapping = {
    'Monday': 'mon',
    'Tuesday': 'tue',
    'Wednesday': 'wed',
    'Thursday': 'thu',
    'Friday': 'fri',
    'Saturday': 'sat',
    'Sunday': 'sun'
}
selected_days_cron = [day_mapping[day] for day in selected_days]  # Преобразуем выбранные дни в формат cron

# 2nd column
# genre choose, discount, check time, check button

# app status display
if st.session_state.running:
    col2.write("<h4>Watcher is running</h4>", unsafe_allow_html=True)
else:
    col2.write("<h4>Watcher is not running</h4>", unsafe_allow_html=True)
    game_tag_id = col2.text_input("Enter game tag id:")

    # Кнопка запуска submit запросов и запуск планировщика
    with col2:
        subcol1, subcol2 = st.columns(2)

        is_discounted = col2.radio("Search for discounted?", options=("yes", "no"), index=0)
        scheduled_time = col2.time_input("Select the time to run the task (e.g., 14:30):", value=dt.time(12, 0), step=300)

        submit_btn = subcol1.button("Submit request")
        run_btn = subcol2.button("Run watcher now")

        if submit_btn:
            query_check()  # Проверяем ввод пользователя
            if st.session_state.running:
                start_watcher()  # Запускаем планировщик
                st.write("Watcher successfully scheduled.")
        elif run_btn:
            query_check()  # Проверяем ввод пользователя
            if st.session_state.running:
                watcher()
                st.write("Watcher successfully started.")



