from flask import Flask, redirect
from healthcheck import HealthCheck, EnvironmentDump
import requests

app = Flask(__name__)

# wrap the flask app and give a heathcheck url
health = HealthCheck(app, "/healthcheck")
envdump = EnvironmentDump(app, "/environment")

@app.route('/')
def main_index():
    return "Ops client: 127.0.0.1:5000/user/"

@app.route('/user/<user>')
def get_user(user):
    r = requests.get('http://crud.staging.fargate.local:5000/user/' + user)
    return "Fetched through the ops_client: " + r.text

@app.route('/ping')
def ping():
    return redirect('/healthcheck')
