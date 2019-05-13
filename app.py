from flask import Flask, redirect
from healthcheck import HealthCheck, EnvironmentDump
import requests
import os

alb = os.getenv('ALB', 'localhost')
service_name = os.getenv('SERVICE_NAME', '-')
service_version = os.getenv('SERVICE_VERSION', '-')
service_environment = os.getenv('SERVICE_ENVIRONMENT', '-')

prefix = ''
if service_name:
    prefix = '/' + service_name


from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

app = Flask(__name__)

plugins = ('ECSPlugin')
xray_recorder.configure(service=service_name, plugins=plugins)
XRayMiddleware(app, xray_recorder)


# wrap the flask app and give a heathcheck url
health = HealthCheck(app, prefix + "/admin/healthcheck")
envdump = EnvironmentDump(app, prefix + "/admin/environment")

@app.route(prefix + '/')
def main_index():
    return 'NAME: %s\nVERSION: %s\nENVIRONMENT: %s\n' % (service_name, service_version, service_environment)

@app.route(prefix + '/user/<user>')
def get_user(user):
    r = requests.get('http://' + alb + '/crud/user/' + user)
    return "Fetched through the ops/client: " + r.text
