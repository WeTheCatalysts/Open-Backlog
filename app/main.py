from flask import Flask, jsonify
from google.cloud import datastore

import actions
import utils

import logging

client = datastore.Client()
key = client.key('Secret', 5634161670881280)
secret = client.get(key)

app = Flask(__name__)
app.config["api_id"] = secret["api_id"]
app.config["api_password"] = secret["api_password"]


@app.template_filter('timesince')
def timesince(date):
    return utils.humanize_timesince(date)


@app.template_filter('markdown')
def markdown(content):
    return utils.applymarkdown(content)



@app.route("/", methods=["GET"])
@utils.returns_html('index.html')
def get_home():
    organisations, errors, success = actions.Organisations(app.config["api_id"], app.config["api_password"]).get_organisations()
    logging.warn(organisations)
    logging.warn(errors)
    logging.warn(success)
    return actions.Organisations(app.config["api_id"], app.config["api_password"]).get_organisations()


@app.route("/organisations", methods=["GET"])
@utils.returns_html('organisations.html')
def get_organisations():
    return actions.Organisations(app.config["api_id"], app.config["api_password"]).get_organisations()


@app.route("/organisations/<organisation_slug>", methods=["GET"])
@utils.returns_html('backlog.html')
def get_organisation(organisation_slug):
    organisations, error, success = actions.Organisations(app.config["api_id"], app.config["api_password"]).get_organisations()
    organisation_found = False
    organisation_api_id = None
    organisation_api_password = None
    if success:
        for organisation in organisations['records']:
            if organisation_slug == organisation['organisationSlug']:
                organisation_found = True
                organisation_api_id = organisation['steinApiId']
                organisation_api_password = organisation['steinApiPassword']
                organisation_name = organisation['organisationName']
    if organisation_found:
        backlog, error, success = actions.Backlog(organisation_api_id, organisation_api_password).get_backlog()
        if success:
            backlog["metadata"]["organisationName"] = organisation_name
            backlog["metadata"]["organisationSlug"] = organisation_slug
        return backlog, error, success
    else:
        return None, 'no_organisation', False


@app.route("/organisations/<organisation_slug>/<item_id>", methods=["GET"])
@utils.returns_html('item.html')
def get_backlog_item(organisation_slug, item_id):
    organisations, error, success = actions.Organisations(app.config["api_id"], app.config["api_password"]).get_organisations()
    organisation_found = False
    organisation_api_id = None
    organisation_api_password = None
    if success:
        for organisation in organisations['records']:
            if organisation_slug == organisation['organisationSlug']:
                organisation_found = True
                organisation_api_id = organisation['steinApiId']
                organisation_api_password = organisation['steinApiPassword']
                organisation_name = organisation['organisationName']
    if organisation_found:
        record, error, success = actions.Backlog(organisation_api_id, organisation_api_password).get_backlog_item(item_id)
        if success:
            record["metadata"]["organisationName"] = organisation_name
            record["metadata"]["organisationSlug"] = organisation_slug
        return record, error, success
    else:
        return None, 'no_record', False


@app.route("/contributors", methods=["GET"])
@utils.returns_html('contributors.html')
def show_contributors():
    return {}, None, True

#@app.route("/", methods=["GET"])
#@utils.returns_html('index.html')
#def get_backlog():
#    return actions.Backlog(app.config).get_backlog()


#@app.route("/api/v1/", methods=["GET"])
#@app.route("/api/v1", methods=["GET"])
#@utils.returns_json
#def api_get_backlog():
#    return actions.Backlog(app.config).get_backlog()


#@app.route("/api/v1/item/<id>", methods=["GET"])
#@app.route("/api/v1/item/id", methods=["GET"])
#@utils.returns_json
#def api_get_backlog_item(id):
#    return actions.Backlog(app.config).get_backlog_item(id)

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]
