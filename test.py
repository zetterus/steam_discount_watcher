import pandas as pd
import streamlit as st

# # Исходный список жанров
# genres = ["Action", "Indie", "Adventure", "Casual", "RPG", "Strategy", "Simulation", "Early Access", "Free to Play", "Sports"]
#
# # Создаем DataFrame из списка жанров
# df = pd.DataFrame({'Жанр': genres}, index=list(range(1, len(genres)+1)))
#
# # # Добавляем столбец с порядковым номером
# # df['Номер'] = range(1, len(df) + 1)
#
# # Отображаем таблицу в Streamlit
# st.dataframe(df)

st.session_state.num = 9

if st.session_state.num == int(st.session_state.num):
    st.write("all ok")
else:
    st.write("smth wrong")
