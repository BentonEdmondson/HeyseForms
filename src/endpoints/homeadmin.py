from flask import Blueprint, render_template, redirect
import sheets_api.sheets as gsheets
import random

homeadmin = Blueprint('homeadmin', __name__)

homeadmin.route('/', methods=["GET"])(
    lambda: redirect('/homeadmin', code=308)
)

@homeadmin.route('/homeadmin', methods=['GET'])
def get_homeadmin():
    interns = gsheets.get_all_interns()
    sub_count = gsheets.get_total_submission_count()
    for intern in interns:
        entries = gsheets.get_intern_entries(intern_email=intern["uniqname"]+"@umich.edu")
        intern["progress"] = len(entries)/sub_count
        intern["submission"] = len(entries)
    return render_template('homeadmin.j2', interns=interns,sub_count=sub_count)