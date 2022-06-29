from flask import Flask, Blueprint, render_template
import sheets_api.sheets as gsheets

settings = Blueprint('settings', __name__)

@settings.route('/settings', methods=['GET'])
def get_settings():
    notif = gsheets.get_supervisor_notifcation(supervisor_email="jjc@umich.edu")
    return render_template(
        'settings.j2',
        notif=notif
    )