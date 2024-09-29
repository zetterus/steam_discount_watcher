import streamlit as st
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time

# Инициализация планировщика
scheduler = BackgroundScheduler()

# Функция для выполнения задачи
def scheduled_task():
    st.session_state.task_message = "Задача выполнена в " + datetime.now().strftime("%H:%M:%S")
    st.rerun()  # Используем st.rerun() вместо устаревшего experimental_rerun()

# Функция для запуска планировщика
def start_scheduler(hour, minute):
    # Запуск планировщика
    if not scheduler.running:
        scheduler.start()

    # Планируем задачу
    scheduler.add_job(
        scheduled_task,
        'cron',
        hour=hour,
        minute=minute
    )
    st.session_state.scheduled = True
    st.rerun()  # Используем st.rerun() для обновления

# Инициализация переменных в session_state
if 'scheduled' not in st.session_state:
    st.session_state.scheduled = False
if 'task_message' not in st.session_state:
    st.session_state.task_message = ""
if 'selected_time' not in st.session_state:
    st.session_state.selected_time = datetime.now().time()

# Интерфейс выбора времени с использованием session_state
st.title("Планировщик задачи")

# Используем сохранённое время из session_state, если оно существует
selected_time = st.time_input("Выберите время выполнения задачи", value=st.session_state.selected_time, step=60)

# Сохраняем выбранное время в session_state при каждом обновлении
st.session_state.selected_time = selected_time

# Кнопка для запуска планировщика
if st.button("Запланировать задачу"):
    hour = selected_time.hour
    minute = selected_time.minute
    start_scheduler(hour, minute)
    st.write(f"Задача запланирована на {hour:02d}:{minute:02d}")

# Сообщение о выполнении задачи
if st.session_state.task_message:
    st.success(st.session_state.task_message)

# Удерживаем приложение активным для выполнения задач
while scheduler.get_jobs():
    time.sleep(1)
