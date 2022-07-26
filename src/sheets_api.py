from __future__ import print_function
from collections import OrderedDict
import datetime
from datetime import date

import os.path

from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from decouple import config

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
PRIVATE_KEY = f"-----BEGIN PRIVATE KEY-----\n{config('private_key')} \n-----END PRIVATE KEY-----\n"
PRIVATE_KEY = PRIVATE_KEY.replace(r'\\','\\')) 

SERVICE_ACCOUNT_INFO = {"type": config('type'),
                        "project_id": config('project_id'),
                        "private_key_id": config('private_key_id'),
                        "private_key": PRIVATE_KEY,
                        "client_email": config('client_email'),
                        "client_id": config('client_id'),
                        "auth_uri": config('auth_uri'),
                        "token_uri": config('token_uri'),
                        "auth_provider_x509_cert_url": config('auth_provider_x509_cert_url'),
                        "client_x509_cert_url": config('client_x509_cert_url')}

print(PRIVATE_KEY)
# The ID of HeyseForms sample spreadsheet.
HEYSE_FORMS_SAMPLE_SPREADSHEET_ID = '1ymUE8AJEEyXvfLML8PNVbs-sI3poYKq1Vw2_HKTR4qw'
EMAIL_COLUMN_NAME = "Email Address"

INTERNSHIP_START_DATE = date(2022,5,2)

def check_credentials(func):
    def wrapper(*args, **kwargs):
        creds = None
        creds = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
        try:
            return func(creds=creds, *args, **kwargs)
        except HttpError as err:
            raise Exception(f"Error while requesting Google Sheet API. Reason: {err.reason}")
    return wrapper


def get_spreadsheet_URL():
    link = f"https://docs.google.com/spreadsheets/d/{HEYSE_FORMS_SAMPLE_SPREADSHEET_ID}/edit#gid=0"
    return link


@check_credentials
def get_total_submission_count(creds: Credentials) -> int:
    """
    Gets start date.
    """
 
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    my_range = "Response!A2"

    data = sheet.values().get(spreadsheetId=HEYSE_FORMS_SAMPLE_SPREADSHEET_ID,
                                range=my_range).execute()
    values = data.get('values')
    date_time_obj = datetime.datetime.strptime(values[0][0], '%m/%d/%Y %H:%M:%S')
    days = abs(date_time_obj.date()-date.today()).days
    
    return (days//7)+1


# def get_total_submission_count():
#     days = abs(INTERNSHIP_START_DATE-date.today()).days
#     return (days//7)+1


@check_credentials
def set_spreadsheet_URL(new_link: str, creds: Credentials):
    try:
        sheet_id = (new_link.split("/d/"))[1].split("/edit")[0]
        if not sheet_id:
            raise Exception()
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        # Test 1 - Response Sheet
        my_range = "Response!A1:Z"
        data = sheet.values().get(spreadsheetId=sheet_id,
                                    range=my_range).execute()
        # Test 2 - Record Sheet
        my_range = "Record!A1:Z"
        data = sheet.values().get(spreadsheetId=sheet_id,
                                    range=my_range).execute()
        
        global HEYSE_FORMS_SAMPLE_SPREADSHEET_ID
        HEYSE_FORMS_SAMPLE_SPREADSHEET_ID=sheet_id
    except HttpError:
        raise Exception("ERROR: The new spreadhseet link doesn't have proper permission or sheet names. Reverted to old link.")
    except:
        raise Exception("ERROR: Could not find the spreadsheet ID. Please check your link.")



@check_credentials
def get_all_intern_entries(creds: Credentials) -> list:
    """
    Gets all the entries of an intern.
    """
    result = []

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    my_range = "Response!A1:Z"

    data = sheet.values().get(spreadsheetId=HEYSE_FORMS_SAMPLE_SPREADSHEET_ID,
                                range=my_range).execute()
    values = data.get('values', [])

    result = []

    if len(values) > 1:
        for row in values[1:]:
            entry = convert_to_dict(values[0], row)
            result.append(entry)
    
    return result


def get_intern_entries(intern_email: str= "", intern_emails: list = []) -> dict:
    try:
        entries = get_all_intern_entries()
        result = []
        for entry in entries:
            if (entry[EMAIL_COLUMN_NAME] == intern_email) or (entry[EMAIL_COLUMN_NAME] in intern_emails):
                result.append(entry)
        return result
    except Exception as e:
        raise e


@check_credentials
def get_all_supervisor_data(creds: Credentials) -> list:
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    my_range = "Record!A1:Z"
    data = sheet.values().get(spreadsheetId=HEYSE_FORMS_SAMPLE_SPREADSHEET_ID,
                                range=my_range, majorDimension="COLUMNS").execute()
    values = data.get('values', [])

    result = []

    if len(values) > 1:
        for row in values[1:]:
            entry = convert_to_dict(values[0], row)
            result.append(entry)
    return result


def get_supervisor_interns(supervisor_email: str) -> dict:
    try:
        supervisors = get_all_supervisor_data()
        result = {}
        for supervisor in supervisors:
            if supervisor["Email"] == supervisor_email:
                interns = []
                if "Interns" in supervisor:
                    interns = supervisor["Interns"].split(", ")
                for intern in interns:
                    result[intern + "@umich.edu"] = {
                        "uniqname": intern,
                    }
        return result
    except Exception as e:
        raise e


def get_all_interns() -> list:
    try:
        supervisors = get_all_supervisor_data()
        check_set = set()
        result = []
        for supervisor in supervisors:
            if "Interns" in supervisor:
                interns = supervisor["Interns"].split(", ")
                for intern in interns:
                    if intern not in check_set:
                        check_set.add(intern)
                        result.append({
                            "uniqname": intern
                        })
        return result
    except Exception as e:
        raise e


def get_supervisor_notifcation(supervisor_email: str) -> bool:
    try:
        supervisors = get_all_supervisor_data()
        for supervisor in supervisors:
            if supervisor["Email"] == supervisor_email:
                if supervisor["Reminders"] == "1":
                    return True
                return False

        return None
    except Exception as e:
        raise e

def get_supervisor_email_list():
    supervisors = get_all_supervisor_data()
    result = []
    for supervisor in supervisors:
        if supervisor["Reminders"] == "1":
                result.append(supervisor["Email"])
    
    return result


@check_credentials
def update_supervisor(supervisor_data: OrderedDict, my_range: str, creds: Credentials):
    service = build('sheets', 'v4', credentials=creds)

    body = {
        "majorDimension": "COLUMNS",
        "values": [list(supervisor_data.values())]
    }

    response = service.spreadsheets().values().update(
            spreadsheetId=HEYSE_FORMS_SAMPLE_SPREADSHEET_ID, range=my_range,
            valueInputOption="USER_ENTERED", body=body).execute()

    return response


def convert_to_dict(keys: list, values: list) -> dict:
    return OrderedDict(zip(keys, values))


if __name__ == '__main__':
    pass
