import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Google Sheets Setup ---
# Define the scope
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Add your credentials file (replace 'your-credentials.json' with your file name)
creds = ServiceAccountCredentials.from_json_keyfile_name("steam-watcher-credentials-db0622d10a00.json", scope)

# Authorize the client sheet
client = gspread.authorize(creds)

# Open the Google Sheet (replace 'your-google-sheet-name' with your sheet name)
sheet = client.open("streamlit_watcher_credentials").sheet1  # Use .sheet1 or specify the sheet name


# Function to load user settings from Google Sheets
def load_user_settings_from_gsheets(username, sheet):
    """
    Load the user settings from Google Sheets.

    :param username: The username for which to load settings.
    :param sheet: The Google Sheets object.
    :return: The settings if found, else an empty dictionary.
    """
    records = sheet.get_all_records()
    print(records)

    # Find and return the user's settings for the specified watcher type
    for row in records:
        print(row['first'])
        if row['first'] == username:
            print(row)

    print("No settings found for the user in Google Sheets.")
    return {}


load_user_settings_from_gsheets(4, sheet)
