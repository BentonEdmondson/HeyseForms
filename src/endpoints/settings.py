from urllib import response
from flask import Flask, Blueprint, render_template, redirect, request
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

@settings.route('/settings/toggleReminder', methods=['POST'])
def toggle_reminder():
    all_supervisor_data = gsheets.get_all_supervisor_data()
    for idx, supervisor in enumerate(all_supervisor_data):
        if supervisor["Email"] == "jjc@umich.edu":
            if request.form.get("toggler") == "on":
                supervisor["Reminders"] = "1"
            else:
                supervisor["Reminders"] = "0"
            print(supervisor)
            range = f"Record!{chr(65+idx+1)}1:{chr(65+idx+1)}4"
            gsheets.update_supervisor(supervisor_data=supervisor, my_range=range)


    return redirect("/settings")