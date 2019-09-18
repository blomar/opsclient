from flask import Flask, redirect
from healthcheck import HealthCheck, EnvironmentDump
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from aws_xray_sdk.core import patch_all

import logging
import json_logging
import sys
import requests
import os

alb = os.getenv('ALB', 'localhost')
service_name = os.getenv('SERVICE_NAME', '-')
service_version = os.getenv('SERVICE_VERSION', '-')
service_environment = os.getenv('SERVICE_ENVIRONMENT', '-')
prefix = ('/%s' % service_name)

# Logging
json_logging.ENABLE_JSON_LOGGING = True
json_logging.init(framework_name='flask')
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [stdout_handler]
logging.basicConfig(
    level=logging.INFO,
    handlers=handlers
)
json_logging.config_root_logger()

app = Flask(__name__)
json_logging.init_request_instrument(app)
LOGGER = logging.getLogger(__name__)
LOGGER.info('start application - %s', service_name)

xray_recorder.configure(service=service_name)
XRayMiddleware(app, xray_recorder)
patch_all()

# wrap the flask app and give a healthcheck url
health = HealthCheck(app, prefix + '/admin/healthcheck')
envdump = EnvironmentDump(app, prefix + '/admin/environment')


@app.route(prefix + '/')
def main_index():
    LOGGER.info('main_index',
                extra={'props': {'name': service_name, 'version': service_version, 'environment': service_environment}})
    return 'NAME: %s\nVERSION: %s\nENVIRONMENT: %s\n' % (service_name, service_version, service_environment)


@app.route(prefix + '/v1/user/<user>')
def get_user_v1(user):
    LOGGER.info('Try http://%s/crud/user/%s', alb, user, extra={'props': {'user': user}})
    response = requests.get('http://' + alb + '/crud/user/' + user)
    return 'Fetched through the ops/client: ' + response.text


@app.route(prefix + '/v2/user/<user>')
def get_user_v2(user):
    LOGGER.info('USER')
    conn_url = 'http://crud.' + service_environment + '.local:5000/crud/user/' + user
    LOGGER.info('Try %s', conn_url, extra={'props': {'user': user}})

    try:
        response = requests.get(conn_url)

        # Consider any status other than 2xx an error
        if not response.status_code // 100 == 2:
            return "Error: Unexpected response {}".format(response)

        return 'Fetched through the ops/client: ' + response.text
    except requests.exceptions.RequestException as e:
        # A serious problem happened, like an SSLError or InvalidURL
        return "Error: {}".format(e)


@app.route(prefix + '/test')
def get_test():
    LOGGER.info('TEST')
    conn_url = 'http://crud.' + service_environment + '.local:5000/crud/'
    LOGGER.info('Try %s', conn_url)
    try:
        response = requests.get(conn_url)

        # Consider any status other than 2xx an error
        if not response.status_code // 100 == 2:
            return "Error: Unexpected response {}".format(response)

        return 'Fetched through the ops/client: ' + response.text
    except requests.exceptions.RequestException as e:
        # A serious problem happened, like an SSLError or InvalidURL
        return "Error: {}".format(e)
