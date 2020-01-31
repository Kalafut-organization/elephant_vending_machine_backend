"""Define all routes for the behavioral experiment server.

Here, all API routes for the experiment server are defined.
Consider splitting into its own package if end up being
a lot of routes.
"""
# Circular import OK here. See https://flask.palletsprojects.com/en/1.1.x/patterns/packages/
# pylint: disable=cyclic-import
from flask import request
from elephant_vending_machine import APP

@APP.route('/')
def index():
    """Responds with basic 'Hello Elephants!' string

    All requests sent to the default route return a simple
    string. This method is intended to be removed once actual
    routes are added.

    Returns:
        HTTP response OK with payload 'Hello Elephants'
    """
    return 'Hello Elephants!'

@APP.route('/run-trial', methods=['GET', 'POST'])
def run_trial():
    """Responds with 'Running {trial_name}' string

    All requests sent to this route should have a trial_name in
    the query string, otherwise a 400 error will be returned

    Returns:
        HTTP response OK or Bad Request with payload 'Running {trial_name}'
    """
    response = ""
    if request.args.get('trial_name') is not None:
        response = 'Running ' + request.args.get('trial_name')
    else:
        response = 'No trial_name specified'
    return response
