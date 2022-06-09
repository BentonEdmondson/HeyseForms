from flask import Flask, Blueprint, render_template

settings = Blueprint('settings', __name__)

@settings.route('/settings', methods=['GET'])
def get_settings():
    return render_template('settings.j2')