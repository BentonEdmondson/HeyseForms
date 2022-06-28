from flask import Flask, Blueprint, render_template, redirect
import sheets_api.sheets as gsheets

responses = Blueprint('responses', __name__)

responses.route('/responses', methods=['GET'])(
    lambda: redirect('/home', code=308)
)

@responses.route('/responses/<uniqname>', methods=['GET'])
def get_default_response(uniqname: str):
    return redirect('/responses/'+uniqname+'/1')

@responses.route('/responses/<uniqname>/<entry>', methods=['GET'])
def get_response(uniqname: str, entry: int):
    entries = gsheets.get_intern_entries(intern_email=uniqname+"@umich.edu")
    return render_template(
        'responses.j2',
        show_entry=entry,
        entries = entries,
        uniqname=uniqname,
        email=uniqname+'@umich.edu'
    )
    