from flask import Flask, Blueprint, render_template, redirect

home = Blueprint('home', __name__)

home.route('/', methods=["GET"])(
    lambda: redirect('/home', code=308)
)

@home.route('/home', methods=['GET'])
def get_home():
    return render_template('home.j2')