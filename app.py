from flask import Flask, request, Response
from healthcheck import HealthCheck, EnvironmentDump
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from aws_xray_sdk.core import patch_all
from prometheus_flask_exporter import PrometheusMetrics

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

#Logging
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

# Metrics
metrics = PrometheusMetrics(app, export_defaults=False, path=prefix + '/admin/metrics', defaults_prefix=service_name,
                            group_by='path', buckets=None, registry=None)

metrics.info('app_info', 'Application info', version=service_version, service_name=service_name,
             service_environment=service_environment)

# wrap the flask app and give a heathcheck url
health = HealthCheck(app, prefix + '/admin/healthcheck')
envdump = EnvironmentDump(app, prefix + '/admin/environment')


@app.route(prefix + '/')
def main_index():
    LOGGER.info('main_index', extra = {'props' : {'name': service_name, 'version': service_version,
                                                  'environment': service_environment}})
    return 'NAME: %s\nVERSION: %s\nENVIRONMENT: %s\n' % (service_name, service_version, service_environment)


@app.route(prefix + '/user/<user>')
def get_user(user):
    LOGGER.info('Try to fetch user: %s', user, extra = {'props': {'user' : user}})
    response = requests.get('http://' + alb + '/' + prefix + '/crud/user/' + user)
    return 'Fetched through the ops/client: ' + response.text


@app.route(prefix + '/random')
def get_random():
    response = requests.get('http://' + alb + '/' + prefix + '/crud/stats')
    LOGGER.info('Random, code %s', response.status_code)
    return response.text, response.status_code
