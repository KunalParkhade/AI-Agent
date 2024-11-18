import gspread
from google.oauth2.service_account import Credentials

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


def connect_to_google_sheets(credentials_path, sheet_id):
    """Authenticate and connect to Google Sheets."""
    try:
        creds = Credentials.from_service_account_file('credentials_path', scopes=SCOPES)
        client = gspread.authorize(creds)
        sheet = client.open_by_key('sheet_id').sheet1
        data = sheet.get_all_records()
        return data
    
    except Exception as e:
        raise Exception(f"Failed to connect to Google Sheets: {e}")