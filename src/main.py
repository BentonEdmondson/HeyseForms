from http.client import responses
from flask import Flask, Blueprint, render_template, redirect, request, url_for, session
from authlib.integrations.flask_client import OAuth
from decouple import config
import sheets_api.sheets as gsheets
import re

app = Flask(__name__, template_folder="./templates")

app.secret_key = '!secret'
app.config.from_object('config')

CONF_URL = 'https://shib-idp-dev.dsc.umich.edu/.well-known/openid-configuration'
oauth = OAuth(app)
oauth.register(
    name='HeyesForms',
    server_metadata_url=CONF_URL,
    client_kwargs={
        "client_id": config('OIDC_CLIENT_ID'),
        "client_secret": config('OIDC_CLIENT_SECRET'),
        "scope": "openid profile email offline_access eduperson_affiliation eduperson_scoped_affiliation",
        "redirect_uris": [
            "https://heyseforms.webplatformsnonprod.umich.edu/auth"
        ],
        "token_endpoint_auth_method": "client_secret_basic",
        "grant_types": [
          "authorization_code",
          "implicit",
          "refresh_token"
        ],
        "response_types": [
          "code",
          "id_token",
          "id_token token",
          "code id_token",
          "code token",
          "code id_token token"
        ]
    }
)



@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return oauth.HeyesForms.authorize_redirect(redirect_uri)

@app.route('/auth')
def auth():
    token = oauth.HeyesForms.authorize_access_token()
    user = token.get('userinfo')
    if user:
        session['user'] = user
    return redirect('/')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


@app.route('/home', methods=['GET'])
def get_home():
    print(session.get('user'))
    interns = gsheets.get_supervisor_interns(supervisor_email="jjc@umich.edu")
    sub_count = gsheets.get_total_submission_count()
    for intern in interns:
        entries = gsheets.get_intern_entries(intern_email=intern["uniqname"]+"@umich.edu")
        intern["progress"] = len(entries)/sub_count
        intern["submission"] = len(entries)
    return render_template('home.j2', interns=interns, sub_count=sub_count)


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
    interns = gsheets.get_supervisor_interns(supervisor_email="jjc@umich.edu")
    notif = gsheets.get_supervisor_notifcation(supervisor_email="jjc@umich.edu")
    link = gsheets.get_spreadsheet_URL()
    return render_template(
        'settings.j2',
        notif=notif,
        interns=interns,
        link = link
    )


@app.route('/settings/addIntern', methods=['POST'])
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


@app.route('/settings/removeIntern', methods=['POST'])
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


@app.route('/settings/toggleReminder', methods=['POST'])
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


@app.route('/settingsadmin', methods=['GET'])
def get_settingsadmin():
    interns = gsheets.get_all_interns()
    notif = gsheets.get_supervisor_notifcation(supervisor_email="jjc@umich.edu")
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


if __name__ == "__main__":
    app.run()