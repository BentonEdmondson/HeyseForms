from flask import Blueprint, render_template, redirect
import sheets_api.sheets as gsheets


gsheet = Blueprint('gsheet', __name__)

gsheet.route('/', methods=["GET"])(
    lambda: redirect('/gsheet', code=308)
)

@gsheet.route('/gsheet', methods=['GET'])
def get_gsheet():
    link = gsheets.get_spreadsheet_URL()
    return render_template('gsheet.j2', link = link)