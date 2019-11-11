from flask import Flask, jsonify

import actions
import utils

import logging

app = Flask(__name__)

app.config.from_envvar('APPLICATION_SETTINGS')


@app.route("/", methods=["GET"])
@utils.returns_html('index.html')
def get_backlog():
    return {"message":"Hello World"}, None, True


@app.route("/api/v1/", methods=["GET"])
@app.route("/api/v1", methods=["GET"])
@utils.returns_json
def api_get_backlog():
    return actions.Backlog(app.config).get_backlog()


@app.route("/api/v1/item/<id>", methods=["GET"])
@app.route("/api/v1/item/id", methods=["GET"])
@utils.returns_json
def api_get_backlog_item(id):
    return actions.Backlog(app.config).get_backlog_item(id)
