from flask import Flask
import requests

app = Flask(__name__)

@app.route('/')
def main_index():
    return "Ops client: 127.0.0.1:5000/user/"

@app.route('/ping')
def ping():
    return ""

@app.route('/user/<user>')
def get_user(user):
    r = requests.get('http://crud:5000/user/' + user)
    return "Fetched through the ops_client: " + r.text
