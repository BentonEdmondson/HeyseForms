from flask import Flask, Blueprint, render_template, redirect
import sheets_api.sheets as gsheets

settings = Blueprint('settings', __name__)

@settings.route('/settings', methods=['GET'])
def get_settings():
    interns = gsheets.get_supervisor_interns(supervisor_email="jjc@umich.edu")
    notif = gsheets.get_supervisor_notifcation(supervisor_email="jjc@umich.edu")
    
    return render_template(
        'settings.j2',
        notif=notif,
        interns=interns
    )