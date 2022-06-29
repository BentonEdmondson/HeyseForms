from flask import Blueprint, render_template, redirect
import sheets_api.sheets as gsheets

home = Blueprint('home', __name__)

home.route('/', methods=["GET"])(
    lambda: redirect('/home', code=308)
)

@home.route('/home', methods=['GET'])
def get_home():
    #interns = gsheets.get_supervisor_interns(supervisor_email="jjc@umich.edu")
    interns = [
        {
            "uniqname": "benton",
            "progress": 0.43
        },
        {
            "uniqname": "amadeus",
            "progress": 0.12
        },
        {
            "uniqname": "lordvader",
            "progress": 1
        }
    ]
    return render_template('home.j2', interns=interns)