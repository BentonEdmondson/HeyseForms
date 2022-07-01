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
    for intern in interns:
        intern["progress"] = random.random()
    return render_template('homeadmin.j2', interns=interns)