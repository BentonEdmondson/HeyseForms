from flask import Flask, Blueprint, render_template
import sheets_api.sheets as gsheets

settingsadmin = Blueprint('settingsadmin', __name__)

@settingsadmin.route('/settingsadmin', methods=['GET'])
def get_settings():
    interns = gsheets.get_all_interns()
    notif = gsheets.get_supervisor_notifcation(supervisor_email="jjc@umich.edu")
    return render_template(
        'settings.j2',
        notif=notif,
        interns=interns
    )