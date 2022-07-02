from flask import Blueprint, redirect, render_template, request
import sheets_api.sheets as gsheets


settingsadmin = Blueprint('settingsadmin', __name__)


@settingsadmin.route('/settingsadmin', methods=['GET'])
def get_settingsadmin():
    # interns = gsheets.get_all_interns()
    interns=[]
    notif = gsheets.get_supervisor_notifcation(supervisor_email="jjc@umich.edu")
    spreadsheet_link = gsheets.get_spreadsheet_URL()
    return render_template(
        'settingsadmin.j2',
        spreadsheet_link=spreadsheet_link,
        notif=notif,
        interns=interns
    )


@settingsadmin.route('/settingsadmin/changeSpreadsheetURL', methods=['POST'])
def update_spreadsheet_link():
    gsheets.set_spreadsheet_URL(request.form.get("spreadsheetLink"))
    return redirect("/settingsadmin")
