from http.client import responses
from flask import Flask, Blueprint, render_template, redirect, request, url_for, session
from flask_crontab import Crontab
from authlib.integrations.flask_client import OAuth
from decouple import config
import send_email
import sheets_api as gsheets
import requests
import re

app = Flask(__name__, template_folder="./templates")
crontab = Crontab(app)
app.secret_key = '!secret'

CONF_URL = 'https://shibboleth.umich.edu/.well-known/openid-configuration'
# CONF_URL = 'https://shib-idp-staging.dsc.umich.edu/.well-known/openid-configuration'
HEYESFORMS_AUTHORIZE_URL = 'https://heyseforms.webplatformsnonprod.umich.edu/auth'
ITS_WEBPAGE = 'https://its.umich.edu/'

oauth = OAuth(app)
oauth.register(
    name='HeyesForms',
    client_id = config('OIDC_CLIENT_ID'),
    client_secret = config('OIDC_CLIENT_SECRET'),
    server_metadata_url=CONF_URL,
    client_kwargs={ 
        "scope": "openid profile email offline_access edumember eduperson"
    }
)

@crontab.job(minute="0", hour="17", day_of_week="FRI")
def schedule_email_reminder():
    send_email.setup()
    send_email.send_reminder_email()

@app.route('/login')
def login():
    redirect_uri = HEYESFORMS_AUTHORIZE_URL
    return oauth.HeyesForms.authorize_redirect(redirect_uri)


@app.route('/auth')
def auth():
    token = oauth.HeyesForms.authorize_access_token()
    user = token.get('userinfo')
    access_token = token['access_token']
    # request to userinfo endpoint
    # r = requests.get(url='https://shib-idp-staging.dsc.umich.edu/idp/profile/oidc/userinfo', params={'access_token':access_token})
    r = requests.get(url='https://shibboleth.umich.edu/idp/profile/oidc/userinfo', params={'access_token':access_token})
    temp = r.json()
    admins = ['alvaradx', 'jeonghin', 'kfliu', 'atharvak', 'oluwake', 'benton']
    if 'edumember_ismemberof' in temp:
        if 'ITS Internship Planning' in temp['edumember_ismemberof']:
            if user:
                session['user'] = user
                session['data'] = temp
                return redirect('/home')    
    elif temp['sub'] in admins:
        if user:
            session['user'] = user
            session['data'] = temp
            return redirect('/home')
    else:
        if user:
            session['user'] = user
        return redirect('/noauth')


def must_be_loggedin(func):
    def checking(**kwargs):
        if 'user' not in session:
            return redirect('/login')
        elif session['user'] is None:
            return redirect('/login')
        elif 'data' not in session:
            return redirect('/noauth')
        elif session['data'] is None:
            return redirect('/noauth')
        elif len(kwargs) == 1:
            return func(kwargs.get('uniqname'))
        elif len(kwargs) == 2:
            return func(kwargs.get('uniqname'), kwargs.get('entry'))
        else:
            return func()
    # this is a fix for overwriting existing endpoint
    checking.__name__ = func.__name__
    return checking


@app.route('/noauth')
def noauth():
    return render_template('noauth.j2', uniqname_user=session['user']['sub'])


@app.route('/logout')
def logout():
    session.pop('user', None)
    if 'data' in session:
        session.pop('data', None)
    return redirect(ITS_WEBPAGE, code=302)


@app.route('/')
@must_be_loggedin
def get_get_home():
    return redirect('/home')


@app.route('/home', methods=['GET'])
@must_be_loggedin
def get_home():
    uniqname_user = session['user']['sub']
    interns = gsheets.get_supervisor_interns(supervisor_email=f"{uniqname_user}@umich.edu")
    entries = gsheets.get_intern_entries(intern_emails=list(interns.keys()))
    sub_count = gsheets.get_total_submission_count()
    for intern in interns:
        interns[intern]["submission"] = 0
    for entry in entries:
        interns[entry[gsheets.EMAIL_COLUMN_NAME]]["submission"] += 1
    return render_template('home.j2', interns=interns, sub_count=sub_count, uniqname_user=uniqname_user)


@app.route('/homeadmin', methods=['GET'])
@must_be_loggedin
def get_homeadmin():
    uniqname_user = session['user']['sub']
    interns = gsheets.get_all_interns()
    sub_count = gsheets.get_total_submission_count()
    for intern in interns:
        entries = gsheets.get_intern_entries(intern_email=intern["uniqname"]+"@umich.edu")
        intern["progress"] = len(entries)/sub_count
        intern["submission"] = len(entries)
    return render_template('homeadmin.j2', interns=interns,sub_count=sub_count, uniqname_user=uniqname_user)


@app.route('/responses/<uniqname>', methods=['GET'])
@must_be_loggedin
def get_default_response(uniqname: str):
    entries = gsheets.get_intern_entries(intern_email=uniqname + "@umich.edu")
    latest_entry_index = str(len(entries))
    return redirect('/responses/' + uniqname + '/' + latest_entry_index)


@app.route('/responses/<uniqname>/<entry>', methods=['GET'])
@must_be_loggedin
def get_response(uniqname: str, entry: int):
    entries = gsheets.get_intern_entries(intern_email=uniqname + "@umich.edu")
    return render_template(
        'responses.j2',
        show_entry=entry,
        entries=entries,
        uniqname=uniqname,
        email=uniqname + '@umich.edu',
        uniqname_user = session['user']['sub']
    )


@app.route('/gsheet', methods=['GET'])
@must_be_loggedin
def get_gsheet():
    link = gsheets.get_spreadsheet_URL()
    return redirect(link, code=302)

@app.route('/responses')
def get_get_responses():
    return redirect('/home', code = 302)


@app.route('/settings', methods=['GET'])
@must_be_loggedin
def get_settings():
    uniqname_user = session['user']['sub']
    interns = gsheets.get_supervisor_interns(supervisor_email=f"{uniqname_user}@umich.edu")
    internss = gsheets.get_supervisor_interns(supervisor_email=f"{uniqname_user}@umich.edu")
    notif = gsheets.get_supervisor_notifcation(supervisor_email=f"{uniqname_user}@umich.edu")
    link = gsheets.get_spreadsheet_URL()
    return render_template(
        'settings.j2',
        notif=notif,
        interns=interns,
        internss=internss,
        link = link,
        uniqname_user = uniqname_user
    )


@app.route('/settings/addIntern', methods=['POST'])
@must_be_loggedin
def add_intern():
    uniqname_user = session['user']['sub']
    all_supervisor_data = gsheets.get_all_supervisor_data()
    for idx, supervisor in enumerate(all_supervisor_data):
        if supervisor["Email"] == f"{uniqname_user}@umich.edu":
            interns = []
            if "Interns" in supervisor:
                interns = supervisor["Interns"].split(", ")
            uniqname_pattern =  re.compile("^(?=.{2,255}$)[a-z]+$")
            if not uniqname_pattern.match(request.form.get("intern_uniqname")):
                raise Exception("Invalid Uniqname!")
            interns.append(request.form.get("intern_uniqname"))
            supervisor["Interns"] = ", ".join(interns)
            range = f"Record!{chr(65+idx+1)}1:{chr(65+idx+1)}4"
            gsheets.update_supervisor(supervisor_data=supervisor, my_range=range)
    return redirect("/settings")


@app.route('/settings/removeIntern', methods=['POST'])
@must_be_loggedin
def remove_intern():
    uniqname_user = session['user']['sub']
    all_supervisor_data = gsheets.get_all_supervisor_data()
    for idx, supervisor in enumerate(all_supervisor_data):
        if supervisor["Email"] == f"{uniqname_user}@umich.edu":
            interns = supervisor["Interns"].split(", ")
            interns.remove(request.form.get("intern_uniqname"))
            supervisor["Interns"] = ", ".join(interns)
            range = f"Record!{chr(65+idx+1)}1:{chr(65+idx+1)}4"
            gsheets.update_supervisor(supervisor_data=supervisor, my_range=range)
    return redirect("/settings")


@app.route('/settings/toggleReminder', methods=['POST'])
@must_be_loggedin
def toggle_reminder():
    uniqname_user = session['user']['sub']
    all_supervisor_data = gsheets.get_all_supervisor_data()
    for idx, supervisor in enumerate(all_supervisor_data):
        if supervisor["Email"] == f"{uniqname_user}@umich.edu":
            if request.form.get("toggler") == "on":
                supervisor["Reminders"] = "1"
            else:
                supervisor["Reminders"] = "0"
            range = f"Record!{chr(65+idx+1)}1:{chr(65+idx+1)}4"
            gsheets.update_supervisor(supervisor_data=supervisor, my_range=range)
    return redirect("/settings")


@app.route('/settingsadmin', methods=['GET'])
@must_be_loggedin
def get_settingsadmin():
    uniqname_user = session['user']['sub']
    interns = gsheets.get_all_interns()
    notif = gsheets.get_supervisor_notifcation(supervisor_email=f"{uniqname_user}@umich.edu")
    spreadsheet_link = gsheets.get_spreadsheet_URL()
    return render_template(
        'settingsadmin.j2',
        spreadsheet_link=spreadsheet_link,
        notif=notif,
        interns=interns,
        uniqname_user=uniqname_user
    )


@app.route('/settingsadmin/changeSpreadsheetURL', methods=['POST'])
@must_be_loggedin
def update_spreadsheet_link():
    gsheets.set_spreadsheet_URL(request.form.get("spreadsheetLink"))
    return redirect("/settingsadmin")


@app.errorhandler(Exception) 
@must_be_loggedin
def invalid_route(e): 
    uniqname_user = session['user']['sub']
    print(e)
    return render_template(
        '404.j2',
        uniqname_user=uniqname_user,
        my_error=e
    )


@app.route('/documentations', methods=['GET'])
@must_be_loggedin
def get_documentations():
    uniqname_user = session['user']['sub']
    return render_template(
        'documentations.j2',
        uniqname_user = uniqname_user
    )

if __name__ == "__main__":
    app.run()
