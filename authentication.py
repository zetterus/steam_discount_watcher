import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import yaml
from yaml.loader import SafeLoader

# Загрузка конфигурации из YAML файла
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Создание хешей паролей (если еще не сделано)
# ... (код для хеширования паролей)

# Инициализация аутентификатора
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    auto_hash=True
)


# Функция для регистрации нового пользователя
def register_user():
    new_user = st.text_input('Username')
    new_password = st.text_input('Password', type='password')
    if st.button('Register'):
        pass


# Функция для восстановления пароля
def reset_password():
    email = st.text_input('Enter your email')
    if st.button('Reset password'):
        pass


# Основной блок кода
if st.session_state['authentication_status']:
    st.write(f'Welcome *{st.session_state["name"]}*')
    # Здесь будет отображаться основное содержимое приложения для авторизованных пользователей
else:
    # Форма авторизации
    result = authenticator.login()
    if result:
        name, authentication_status, username = result
    else:
        # Обработка случая, когда авторизация не удалась
        st.error('Ошибка авторизации')

    # Если авторизация не прошла, предлагаем зарегистрироваться или восстановить пароль
    if authentication_status == False:
        st.error('Username/password is incorrect')
        if st.button('Register'):
            register_user()
        if st.button('Forgot password?'):
            reset_password()
