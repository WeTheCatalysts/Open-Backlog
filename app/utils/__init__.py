from flask import Response, render_template
from functools import wraps

import json
import markdown

import constants

import logging


STRUCTURES = {
    "backlog": {
        "description": "markdown",
        "shortDescription": "markdown",
        "blogURL": "commaseparated",
        "additionalInfoURL": "commaseparated",
        "blogURL": "commaseparated",
        "lifeEvents": "commaseparated",
        "servicePatterns": "commaseparated",
        "beneficiaries": "commaseparated",
        "suppliers": "commaseparated",
        "workingWith": "commaseparated",
        "sameAs": "commaseparated",
        "latestProjectUpdate": "markdown"
    }
}

def applymarkdown(content):
    if content:
        return markdown.markdown(content)
    else:
        return content


def commaseparated_to_array(content):
    array = []
    if content:
        if ',' in content:
            array = content.split(',')
        else:
            array.append(content)
        array = [item.strip() for item in array]
    return array


def action_unwrapper(action_response, response_format='json', template_name=None):
    content = action_response[0]
    error_content = action_response[1]
    success = action_response[2]
    if success:
        if response_format == 'json':
            return json_response(content)
        else:
            if content['datatype'] in STRUCTURES:
                structure = STRUCTURES[content['datatype']]
                for record in content['records']:
                    for field in record:
                        if field in structure:
                            if structure[field] == 'markdown':
                                record[field] = applymarkdown(record[field])
                            if structure[field] == 'commaseparated':
                                record[field] = commaseparated_to_array(record[field])
            return html_response(content, template_name=template_name)
    else:
        if response_format == 'json':
            return json_response(error_content, error=True)
        else:
            return html_response(error_content, template_name='error.html')


def returns_json(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        return action_unwrapper(f(*args, **kwargs))
    return decorated


def returns_html(template_name):
    def render_html(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            return action_unwrapper(f(*args, **kwargs), response_format='html', template_name=template_name)
        return decorated
    return render_html


def json_response(json_data, error=False):
    data = json.dumps(json_data)
    if error:
        response = Response(data, json_data['status'])
    else:
        response = Response(data)
    response.headers['Content-Type'] = 'application/vnd.openbacklog.v{version}+json'.format(
        version=constants.VERSION)
    return response


def html_response(content, template_name='notemplate.html'):
    return render_template(template_name, **content)


def error_response(error_condition):
    data = constants.ERRORS[error_condition]
    data['instance'] = request.path
    data['method'] = request.method
    return json_response(data, error=True)
