from flask import Flask, redirect
from healthcheck import HealthCheck, EnvironmentDump
import requests
import os

app = Flask(__name__)

# wrap the flask app and give a heathcheck url
health = HealthCheck(app, "/healthcheck")
envdump = EnvironmentDump(app, "/environment")

appenv = os.getenv('APP_ENV', '.staging.fargate.local')

@app.route('/')
def main_index():
    return 'Ops client: APP_ENV: ' + appenv

@app.route('/user/<user>')
def get_user(user):
    r = requests.get('http://crud' + appenv + ':5000/user/' + user)
    return "Fetched through the ops_client: " + r.text

@app.route('/ping')
def ping():
    return redirect('/healthcheck')
