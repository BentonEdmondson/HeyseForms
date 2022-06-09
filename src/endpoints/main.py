from flask import Flask
from home import home
from responses import responses
from settings import settings
from api import api

app = Flask(__name__, template_folder="../templates")

app.register_blueprint(home)
app.register_blueprint(responses)
app.register_blueprint(settings)
app.register_blueprint(api)

if __name__ == "__main__":
    app.run()