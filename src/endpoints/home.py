from flask import Blueprint, render_template, redirect
import sheets_api.sheets as gsheets

home = Blueprint('home', __name__)

home.route('/', methods=["GET"])(
    lambda: redirect('/home', code=308)
)

@home.route('/home', methods=['GET'])
def get_home():
    interns = gsheets.get_supervisor_interns(supervisor_email="jjc@umich.edu")
    entries = gsheets.get_intern_entries(intern_emails=list(interns.keys()))
    sub_count = gsheets.get_total_submission_count()
    for entry in entries:
        if "submission" in interns[entry[gsheets.EMAIL_COLUMN_NAME]].keys():
            interns[entry[gsheets.EMAIL_COLUMN_NAME]]["submission"] += 1
        else:
            interns[entry[gsheets.EMAIL_COLUMN_NAME]]["submission"] = 1
    return render_template('home.j2', interns=interns, sub_count=sub_count)
