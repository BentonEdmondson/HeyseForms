from flask import Blueprint, render_template, redirect, request
import re
import sheets_api.sheets as gsheets


settings = Blueprint('settings', __name__)


@settings.route('/settings', methods=['GET'])
def get_settings():
    interns = gsheets.get_supervisor_interns(supervisor_email="jjc@umich.edu")
    internss = gsheets.get_supervisor_interns(supervisor_email="jjc@umich.edu")
    notif = gsheets.get_supervisor_notifcation(supervisor_email="jjc@umich.edu")
    link = gsheets.get_spreadsheet_URL()
    return render_template(
        'settings.j2',
        notif=notif,
        interns=interns,
        internss=internss,
        link = link
    )


@settings.route('/settings/addIntern', methods=['POST'])
def add_intern():
    all_supervisor_data = gsheets.get_all_supervisor_data()
    for idx, supervisor in enumerate(all_supervisor_data):
        if supervisor["Email"] == "jjc@umich.edu":
            interns = supervisor["Interns"].split(", ")
            uniqname_pattern =  re.compile("^(?=.{2,255}$)[a-z]+$")
            if not uniqname_pattern.match(request.form.get("intern_uniqname")):
                print("Invalid Uniqname!")
                return redirect("/settings")
            interns.append(request.form.get("intern_uniqname"))
            supervisor["Interns"] = ", ".join(interns)
            range = f"Record!{chr(65+idx+1)}1:{chr(65+idx+1)}4"
            gsheets.update_supervisor(supervisor_data=supervisor, my_range=range)
    return redirect("/settings")


@settings.route('/settings/removeIntern', methods=['POST'])
def remove_intern():
    all_supervisor_data = gsheets.get_all_supervisor_data()
    for idx, supervisor in enumerate(all_supervisor_data):
        if supervisor["Email"] == "jjc@umich.edu":
            interns = supervisor["Interns"].split(", ")
            interns.remove(request.form.get("intern_uniqname"))
            supervisor["Interns"] = ", ".join(interns)
            range = f"Record!{chr(65+idx+1)}1:{chr(65+idx+1)}4"
            gsheets.update_supervisor(supervisor_data=supervisor, my_range=range)
    return redirect("/settings")


@settings.route('/settings/toggleReminder', methods=['POST'])
def toggle_reminder():
    all_supervisor_data = gsheets.get_all_supervisor_data()
    for idx, supervisor in enumerate(all_supervisor_data):
        if supervisor["Email"] == "jjc@umich.edu":
            if request.form.get("toggler") == "on":
                supervisor["Reminders"] = "1"
            else:
                supervisor["Reminders"] = "0"
            range = f"Record!{chr(65+idx+1)}1:{chr(65+idx+1)}4"
            gsheets.update_supervisor(supervisor_data=supervisor, my_range=range)
    return redirect("/settings")
