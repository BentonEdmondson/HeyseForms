from flask import Flask, Blueprint, render_template

settingsadmin = Blueprint('settingsadmin', __name__)

@settingsadmin.route('/settingsadmin', methods=['GET'])
def get_settings():
    return render_template('settingsadmin.j2')