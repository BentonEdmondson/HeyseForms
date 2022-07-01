from http.client import responses
from flask import Flask
from endpoints import home, responses, settings, api, settingsadmin, homeadmin

app = Flask(__name__, template_folder="./templates")

app.register_blueprint(home.home)
app.register_blueprint(homeadmin.homeadmin)
app.register_blueprint(responses.responses)
app.register_blueprint(settings.settings)
app.register_blueprint(settingsadmin.settingsadmin)
app.register_blueprint(api.api)

if __name__ == "__main__":
    app.run()