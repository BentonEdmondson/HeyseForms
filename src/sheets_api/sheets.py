from __future__ import print_function

import os.path
from typing import OrderedDict

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'service.json'

# The ID of HeyseForms sample spreadsheet.
HEYSE_FORMS_SAMPLE_SPREADSHEET_ID = '1ymUE8AJEEyXvfLML8PNVbs-sI3poYKq1Vw2_HKTR4qw'
EMAIL_COLUMN_NAME = "Email Address"

def check_credentials(func):
    def wrapper(*args, **kwargs):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(SERVICE_ACCOUNT_FILE):
            creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            return func(creds=creds, *args, **kwargs)
        
        print("Could not find service account credentials.")

    return wrapper


@check_credentials
def get_all_intern_entries(creds: Credentials) -> list:
    """
    Gets all the entries of an intern.
    """
    try:
        result = []

        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        my_range = "Response!A1:E"

        data = sheet.values().get(spreadsheetId=HEYSE_FORMS_SAMPLE_SPREADSHEET_ID,
                                    range=my_range).execute()
        values = data.get('values', [])

        result = []

        if len(values) > 1:
            for row in values[1:]:
                entry = convert_to_dict(values[0], row)
                result.append(entry)
        
        return result

    except HttpError as err:
        print(err)
        return


def get_intern_entries(intern_email: str) -> dict:
    entries = get_all_intern_entries()
    result = []
    for entry in entries:
        if entry[EMAIL_COLUMN_NAME] == intern_email:
            result.append(entry)
    return result


@check_credentials
def get_all_supervisor_data(creds: Credentials) -> list:
    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()

        my_range = "Record!A1:D"
        data = sheet.values().get(spreadsheetId=HEYSE_FORMS_SAMPLE_SPREADSHEET_ID,
                                    range=my_range, majorDimension="COLUMNS").execute()
        values = data.get('values', [])

        result = []

        if len(values) > 1:
            for row in values[1:]:
                entry = convert_to_dict(values[0], row)
                result.append(entry)
        
        return result

    except HttpError as err:
        print(err)
        return


def get_supervisor_interns(supervisor_email: str) -> list:
    supervisors = get_all_supervisor_data()
    result = []
    for supervisor in supervisors:
        if supervisor["Email"] == supervisor_email:
            interns = supervisor["Interns"].split(", ")
            for intern in interns:
                result.append({
                    "uniqname": intern
                })
    return result

def get_all_interns() -> list:
    supervisors = get_all_supervisor_data()
    result = []
    for supervisor in supervisors:
        interns = supervisor["Interns"].split(", ")
        for intern in interns:
            result.append({
                "uniqname": intern
            })
    return result


def get_supervisor_notifcation(supervisor_email: str) -> bool:
    supervisors = get_all_supervisor_data()
    for supervisor in supervisors:
        if supervisor["Email"] == supervisor_email:
            if supervisor["Reminders"] == "1":
                return True
            return False

    return None

def convert_to_dict(keys: list, values: list) -> dict:
    return OrderedDict(zip(keys, values))


if __name__ == '__main__':
    entries = get_intern_entries(intern_email="atharvak@umich.edu")
    print(entries)
    supervisor = get_supervisor_notifcation(supervisor_email="dheyse@umich.edu")
    print(supervisor)