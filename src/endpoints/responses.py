from flask import Flask, Blueprint, render_template, redirect

responses = Blueprint('responses', __name__)

responses.route('/responses', methods=['GET'])(
    lambda: redirect('/home', code=308)
)

@responses.route('/responses/<uniqname>', methods=['GET'])
def get_default_response(uniqname: str):
    return redirect('/responses/'+uniqname+'/1')

@responses.route('/responses/<uniqname>/<entry>', methods=['GET'])
def get_response(uniqname: str, entry: int):
    return render_template(
        'responses.j2',
        uniqname=uniqname,
        email=uniqname+'@umich.edu'
    )