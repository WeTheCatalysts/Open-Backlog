from flask import Response, render_template
from functools import wraps

import json
import datetime
import math
import markdown

import constants

import logging


STRUCTURES = {
    "backlog": {
        "blogURL": "commaseparated",
        "additionalInfoURL": "commaseparated",
        "blogURL": "commaseparated",
        "lifeEvents": "commaseparated",
        "servicePatterns": "commaseparated",
        "beneficiaries": "commaseparated",
        "suppliers": "commaseparated",
        "workingWith": "commaseparated",
        "sameAs": "commaseparated",
        "createdAt": "datetime",
        "updatedAt": "datetime"
    },
    "record": {
        "blogURL": "commaseparated",
        "additionalInfoURL": "commaseparated",
        "blogURL": "commaseparated",
        "lifeEvents": "commaseparated",
        "servicePatterns": "commaseparated",
        "beneficiaries": "commaseparated",
        "suppliers": "commaseparated",
        "workingWith": "commaseparated",
        "sameAs": "commaseparated",
        "createdAt": "datetime",
        "updatedAt": "datetime"
    }

}

def humanize_timesince(date):
    delta = datetime.datetime.now() - date

    num_years = math.floor(delta.days / 365)
    if (num_years >= 1):
        if num_years == 1:
            return str(num_years) + " year ago"
        else:
            return str(num_years) + " years ago"

    num_weeks = math.floor(delta.days / 7)
    if (num_weeks >= 1):
        if num_weeks == 1:
            return str(num_weeks) + " week ago"
        else:
            return str(num_weeks) + " weeks ago"

    if (delta.days >= 1):
        if delta.days == 1:
            return str(delta.days) +  " day ago"
        else:
            return str(delta.days) +  " days ago"

    num_hours = math.floor(delta.seconds / 3600)
    if (num_hours >= 1):
        return str(num_hours) +  " hour ago"
    else:
        return str(num_hours) +  " hours ago"

    num_minutes = math.floor(delta.seconds / 60)
    if (num_minutes >= 1):
        return str(num_minutes) +  " minute ago"
    else:
        return str(num_minutes) +  " minutes ago"

    return "just a few seconds ago"


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
            if isinstance(content, str):
                array.append(content)
            else:
                array = content
        array = [item.strip() for item in array]
    return array

def from_iso_datetime(content):
    if isinstance(content, str):
        try:
            return datetime.datetime.strptime(content, '%Y-%m-%dT%H:%M:%S.%fZ')
        except:
            return None
    else:
        return content

def transform_record(record, structure):
    for field in record:
        if field in structure:
            if structure[field] == 'commaseparated':
                record[field] = commaseparated_to_array(record[field])
            if structure[field] == 'datetime':
                record[field] = from_iso_datetime(record[field])
    return record


def action_unwrapper(action_response, response_format='json', template_name=None):
    content = action_response[0]
    error_content = action_response[1]
    success = action_response[2]
    if success:
        if response_format == 'json':
            return json_response(content)
        else:
            transformable_content = content.copy()
            if 'datatype' in content:
                if content['datatype'] in STRUCTURES:
                    structure = STRUCTURES[content['datatype']]
                    if 'record' in transformable_content:
                        transformable_content['record'] = transform_record(transformable_content['record'], structure)
                    else:
                        for record in transformable_content['records']:
                            record = transform_record(record, structure)
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
