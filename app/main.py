from flask import Flask, jsonify

import actions
import utils

import logging

app = Flask(__name__)
app.config.from_envvar('APPLICATION_SETTINGS')


@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/api/v1")
@app.route("/api/v1/")
@utils.returns_json
def api_get_backlog():
    return actions.Backlog(app.config).get_backlog()
