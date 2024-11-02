import datetime
import time
import os
import datetime as dt
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from werkzeug.security import generate_password_hash, check_password_hash
import json


# scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
# client = gspread.authorize(creds)
# sheet = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"]).sheet1
#
#
# users = sheet.get_all_records()
# print(users)


st.write({'user_id': '', 'game_tag_id': 122, 'scheduled_time_w': '12:00', 'selected_days_cron': ['tue', 'wed'], 'scheduled_time': '13:00', 'selected_days': ['Tuesday', 'Wednesday'], 'is_discounted': 'yes', 'game_tag': '', 'selected_days_w': None, 'scheduled_time_g': '12:00', 'selected_days_g': None, 'page_reloaded': True, 'is_authenticated': True, 'is_discounted_index': 0, 'running': False, 'username': 'zetter'})

# print(json.loads())
print(json.dumps("{user_id: , game_tag_id: 122, scheduled_time_w: 1900-01-01 12:00:00, selected_days_cron: ['tue', 'wed'], scheduled_time: 13:00:00, selected_days: ['Tuesday', 'Wednesday'], is_discounted: yes, game_tag: , selected_days_w: None, scheduled_time_g: 1900-01-01 12:00:00, selected_days_g: None, page_reloaded: True, is_authenticated: True, is_discounted_index: 0, running: False, username: zetter}"))



