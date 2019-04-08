from flask import Flask, redirect
from healthcheck import HealthCheck, EnvironmentDump
import requests
import os

alb = os.getenv('ALB', 'localhost')
service_name = os.getenv('SERVICE_NAME', '')

prefix = ''
if service_name:
    prefix = '/' + service_name

app = Flask(__name__)

# wrap the flask app and give a heathcheck url
health = HealthCheck(app, prefix + "/healthcheck")
envdump = EnvironmentDump(app, prefix + "/environment")

appenv = os.getenv('APP_ENV', '.staging.fargate.local')

@app.route(prefix + '/')
def main_index():
    return 'Ops client: APP_ENV: ' + appenv

@app.route(prefix + '/user/<user>')
def get_user(user):
    r = requests.get('http://' + alb + '/crud/user/' + user)
    return "Fetched through the ops_client: " + r.text
