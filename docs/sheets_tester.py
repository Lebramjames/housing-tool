# %%
import gspread
from google.oauth2.service_account import Credentials

# Define the Google Sheets scope
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Load credentials from the service account file
creds = Credentials.from_service_account_file("google_service_account.json", scopes=SCOPES)

# Authorize the gspread client
client = gspread.authorize(creds)

# Open the spreadsheet by its ID (more reliable than by name)
spreadsheet = client.open_by_key("1rWa4ExIS3I7S4eb-jTp8CuJk-NXVV7BeEp2k_drWAUc")

# Select the first worksheet (or by name if you prefer)
worksheet = spreadsheet.get_worksheet(0)

# Test write
worksheet.append_row(["Hello", "Amsterdam", "2025-07-11"])
print("Row added successfully.")
