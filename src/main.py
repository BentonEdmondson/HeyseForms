from http.client import responses
from flask import Flask, Blueprint, render_template, redirect, request, url_for, session
from authlib.integrations.flask_client import OAuth
from decouple import config
import sheets_api.sheets as gsheets
import re

app = Flask(__name__, template_folder="./templates")

app.secret_key = '!secret'

CONF_URL = 'https://shibboleth.umich.edu/.well-known/openid-configuration'
HEYESFORMS_AUTHORIZE_URL = 'https://heyseforms.webplatformsnonprod.umich.edu/auth'

oauth = OAuth(app)
oauth.register(
    name='HeyesForms',
    client_id = config('OIDC_CLIENT_ID'),
    client_secret = config('OIDC_CLIENT_SECRET'),
    server_metadata_url=CONF_URL,
    client_kwargs={
        "scope": "openid profile email offline_access eduperson_affiliation eduperson_scoped_affiliation"
    }
)



@app.route('/login')
def login():
    redirect_uri = HEYESFORMS_AUTHORIZE_URL
    return oauth.HeyesForms.authorize_redirect(redirect_uri)


@app.route('/auth')
def auth():
    token = oauth.HeyesForms.authorize_access_token()
    user = token.get('userinfo')
    if user:
        session['user'] = user
    return redirect('/home')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


@app.route('/home', methods=['GET'])
def get_home():
    user = session.get('user')
    global uniqname 
    uniqname= user['sub']
    interns = gsheets.get_supervisor_interns(supervisor_email=f"{uniqname}@umich.edu")
    entries = gsheets.get_intern_entries(intern_emails=list(interns.keys()))
    sub_count = gsheets.get_total_submission_count()
    for entry in entries:
        if "submission" in interns[entry[gsheets.EMAIL_COLUMN_NAME]].keys():
            interns[entry[gsheets.EMAIL_COLUMN_NAME]]["submission"] += 1
        else:
            interns[entry[gsheets.EMAIL_COLUMN_NAME]]["submission"] = 1
    return render_template('home.j2', interns=interns, sub_count=sub_count, uniqname=uniqname)


@app.route('/homeadmin', methods=['GET'])
def get_homeadmin():
    interns = gsheets.get_all_interns()
    sub_count = gsheets.get_total_submission_count()
    for intern in interns:
        entries = gsheets.get_intern_entries(intern_email=intern["uniqname"]+"@umich.edu")
        intern["progress"] = len(entries)/sub_count
        intern["submission"] = len(entries)
    return render_template('homeadmin.j2', interns=interns,sub_count=sub_count)


@app.route('/responses/<uniqname>', methods=['GET'])
def get_default_response(uniqname: str):
    return redirect('/responses/' + uniqname + '/1')


@app.route('/responses/<uniqname>/<entry>', methods=['GET'])
def get_response(uniqname: str, entry: int):
    entries = gsheets.get_intern_entries(intern_email=uniqname + "@umich.edu")
    return render_template(
        'responses.j2',
        show_entry=entry,
        entries=entries,
        uniqname=uniqname,
        email=uniqname + '@umich.edu'
    )


@app.route('/gsheet', methods=['GET'])
def get_gsheet():
    link = gsheets.get_spreadsheet_URL()
    return render_template('gsheet.j2', link = link)


@app.route('/settings', methods=['GET'])
def get_settings():
    interns = gsheets.get_supervisor_interns(supervisor_email=f"{uniqname}@umich.edu")
    internss = gsheets.get_supervisor_interns(supervisor_email=f"{uniqname}@umich.edu")
    notif = gsheets.get_supervisor_notifcation(supervisor_email=f"{uniqname}@umich.edu")
    link = gsheets.get_spreadsheet_URL()
    return render_template(
        'settings.j2',
        notif=notif,
        interns=interns,
        internss=internss,
        link = link
    )


@app.route('/settings/addIntern', methods=['POST'])
def add_intern():
    all_supervisor_data = gsheets.get_all_supervisor_data()
    for idx, supervisor in enumerate(all_supervisor_data):
        if supervisor["Email"] == f"{uniqname}@umich.edu":
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


@app.route('/settings/removeIntern', methods=['POST'])
def remove_intern():
    all_supervisor_data = gsheets.get_all_supervisor_data()
    for idx, supervisor in enumerate(all_supervisor_data):
        if supervisor["Email"] == f"{uniqname}@umich.edu":
            interns = supervisor["Interns"].split(", ")
            interns.remove(request.form.get("intern_uniqname"))
            supervisor["Interns"] = ", ".join(interns)
            range = f"Record!{chr(65+idx+1)}1:{chr(65+idx+1)}4"
            gsheets.update_supervisor(supervisor_data=supervisor, my_range=range)
    return redirect("/settings")


@app.route('/settings/toggleReminder', methods=['POST'])
def toggle_reminder():
    all_supervisor_data = gsheets.get_all_supervisor_data()
    for idx, supervisor in enumerate(all_supervisor_data):
        if supervisor["Email"] == f"{uniqname}@umich.edu":
            if request.form.get("toggler") == "on":
                supervisor["Reminders"] = "1"
            else:
                supervisor["Reminders"] = "0"
            range = f"Record!{chr(65+idx+1)}1:{chr(65+idx+1)}4"
            gsheets.update_supervisor(supervisor_data=supervisor, my_range=range)
    return redirect("/settings")


@app.route('/settingsadmin', methods=['GET'])
def get_settingsadmin():
    interns = gsheets.get_all_interns()
    notif = gsheets.get_supervisor_notifcation(supervisor_email=f"{uniqname}@umich.edu")
    spreadsheet_link = gsheets.get_spreadsheet_URL()
    return render_template(
        'settingsadmin.j2',
        spreadsheet_link=spreadsheet_link,
        notif=notif,
        interns=interns
    )


@app.route('/settingsadmin/changeSpreadsheetURL', methods=['POST'])
def update_spreadsheet_link():
    gsheets.set_spreadsheet_URL(request.form.get("spreadsheetLink"))
    return redirect("/settingsadmin")


@app.errorhandler(404) 
def invalid_route(e): 
    return render_template('404.j2')

if __name__ == "__main__":
    app.run()
