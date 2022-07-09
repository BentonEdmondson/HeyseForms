from http.client import responses
from flask import Flask, render_template
from endpoints import home, responses, settings, api, settingsadmin, homeadmin,gsheet

app = Flask(__name__, template_folder="./templates")

app.register_blueprint(home.home)
app.register_blueprint(homeadmin.homeadmin)
app.register_blueprint(responses.responses)
app.register_blueprint(settings.settings)
app.register_blueprint(settingsadmin.settingsadmin)
app.register_blueprint(gsheet.gsheet)
app.register_blueprint(api.api)

@app.errorhandler(404) 
def invalid_route(e): 
    return render_template('404.j2')

if __name__ == "__main__":
    app.run()