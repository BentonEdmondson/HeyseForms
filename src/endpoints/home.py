from flask import Blueprint, render_template, redirect
import sheets_api.sheets as gsheets

home = Blueprint('home', __name__)

home.route('/', methods=["GET"])(
    lambda: redirect('/home', code=308)
)

@home.route('/home', methods=['GET'])
def get_home():
    interns = gsheets.get_supervisor_interns(supervisor_email="jjc@umich.edu")
    sub_count = gsheets.get_total_submission_count()
    for intern in interns:
        entries = gsheets.get_intern_entries(intern_email=intern["uniqname"]+"@umich.edu")
        intern["progress"] = len(entries)/sub_count
        intern["submission"] = len(entries)
    return render_template('home.j2', interns=interns, sub_count=sub_count)
