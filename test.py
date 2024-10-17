import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define the scope
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Add your credentials file
creds = ServiceAccountCredentials.from_json_keyfile_name("steam-watcher-credentials-db0622d10a00.json", scope)

# Authorize the clientsheet
client = gspread.authorize(creds)

# Get the instance of the Spreadsheet
sheet = client.open("streamlit_watcher_credentials").sheet1

# Define a function to write data
def write_to_sheet(data):
    # Assuming `data` is a list of values to write to the sheet
    sheet.append_row(data)
    st.success("Data written to Google Sheets!")

# UI for entering data
st.title("Google Sheets Writer")

input_data = [st.text_input(f"Enter value for column {i+1}") for i in range(5)]

if st.button("Submit"):
    write_to_sheet(input_data)

# Read from the sheet to confirm it works
st.write("Current data in the sheet:")
st.dataframe(sheet.get_all_records())
