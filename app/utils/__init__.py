from flask import Response
from functools import wraps

import json

import constants
#import errors
#import models

import logging


def json_response(json_data, error=False):
    data = json.dumps(json_data)
    if error:
        response = Response(data, json_data['status'])
    else:
        response = Response(data)
    response.headers['Content-Type'] = 'application/vnd.openbacklog.v{version}+json'.format(
        version=constants.VERSION)
    return response


def action_unwrapper(action_response):
    content = action_response[0]
    error_content = action_response[1]
    success = action_response[2]
    if success:
        return json_response(content)
    else:
        return json_response(error_content, error=True)


def returns_json(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        return action_unwrapper(f(*args, **kwargs))
    return decorated


def error_response(error_condition):
    data = constants.ERRORS[error_condition]
    data['instance'] = request.path
    data['method'] = request.method
    return json_response(data, error=True)
