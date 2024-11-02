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

d = dt.datetime.strptime("12:11", "%H:%M")

print(d)
