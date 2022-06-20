from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID of HeyseForms sample spreadsheet.
HEYSE_FORMS_SAMPLE_SPREADSHEET_ID = '1XU0bb1FJIBJdvAWPYX-tDECYBmYVw01GNgNTDx9B7Do'
EMAIL_COLUMN_INDEX = 1
INTERNS_COLUMN_INDEX = 3

def check_credentials(func):
    def wrapper(*args, **kwargs):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        return func(creds=creds, *args, **kwargs)
    return wrapper


@check_credentials
def get_intern_entries(intern_email: str, creds: Credentials) -> list:
    """
    Gets all the entries of an intern.
    """
    try:
        result = []

        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        my_range = "Response!A2:E"

        data = sheet.values().get(spreadsheetId=HEYSE_FORMS_SAMPLE_SPREADSHEET_ID,
                                    range=my_range).execute()
        values = data.get('values', [])

        for row in values:
            if row[EMAIL_COLUMN_INDEX] == intern_email:
                result.append(row)

        return result

    except HttpError as err:
        print(err)
        return


@check_credentials
def get_all_supervisor_data(creds: Credentials) -> list:
    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()

        my_range = "Record!A1:D"
        data = sheet.values().get(spreadsheetId=HEYSE_FORMS_SAMPLE_SPREADSHEET_ID,
                                    range=my_range, majorDimension="COLUMNS").execute()
        values = data.get('values', [])
        
        return values

    except HttpError as err:
        print(err)
        return


def get_supervisor_interns(supervisor_email: str) -> list:
    values = get_all_supervisor_data()
    for row in values:
        if row[EMAIL_COLUMN_INDEX] == supervisor_email:
            return row[INTERNS_COLUMN_INDEX].split(", ")

    return []


def get_supervisor_notifcation(supervisor_email: str) -> bool:
    values = get_all_supervisor_data()
    for row in values:
        if row[EMAIL_COLUMN_INDEX] == supervisor_email:
            if row[2] == "1":
                return True
            return False

    return None


if __name__ == '__main__':
    entries = get_intern_entries(intern_email="atharvak@umich.edu")
    print(entries)
    supervisor = get_supervisor_notifcation(supervisor_email="dheyse@umich.edu")
    print(supervisor)