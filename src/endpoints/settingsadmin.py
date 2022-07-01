from flask import Flask, Blueprint, render_template
import sheets_api.sheets as gsheets

settingsadmin = Blueprint('settingsadmin', __name__)

@settingsadmin.route('/settingsadmin', methods=['GET'])
def get_settings():
    interns = gsheets.get_all_interns()
    return render_template(
        'settingsadmin.j2',
        interns=interns
    )