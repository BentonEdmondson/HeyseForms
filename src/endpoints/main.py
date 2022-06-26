from flask import Flask
from home import home
from responses import responses
from settings import settings
from settingsadmin import settingsadmin
from api import api

app = Flask(__name__, template_folder="../templates")

app.register_blueprint(home)
app.register_blueprint(responses)
app.register_blueprint(settings)
app.register_blueprint(settingsadmin)
app.register_blueprint(api)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
