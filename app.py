from flask import Flask, redirect
from healthcheck import HealthCheck, EnvironmentDump
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from aws_xray_sdk.core import patch_all

import logging
import sys
import requests
import os

alb = os.getenv('ALB', 'localhost')
service_name = os.getenv('SERVICE_NAME', '-')
service_version = os.getenv('SERVICE_VERSION', '-')
service_environment = os.getenv('SERVICE_ENVIRONMENT', '-')
prefix = ('/%s' % service_name)

#Logging
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [stdout_handler]
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(lineno)d:%(name)-8s %(message)s',
    handlers=handlers
)
LOGGER = logging.getLogger(__name__)

app = Flask(__name__)
LOGGER.info('start application - %s', service_name)

xray_recorder.configure(service=service_name)
XRayMiddleware(app, xray_recorder)
patch_all()

# wrap the flask app and give a heathcheck url
health = HealthCheck(app, prefix + '/admin/healthcheck')
envdump = EnvironmentDump(app, prefix + '/admin/environment')

@app.route(prefix + '/')
def main_index():
    LOGGER.info('main_index')
    return 'NAME: %s\nVERSION: %s\nENVIRONMENT: %s\n' % (service_name, service_version, service_environment)

@app.route(prefix + '/user/<user>')
def get_user(user):
    LOGGER.info('Try to fetch user: %s', user)
    r = requests.get('http://' + alb + '/crud/user/' + user)
    return 'Fetched through the ops/client: ' + r.text
