"""Define all routes for the behavioral experiment server.

Here, all API routes for the experiment server are defined.
Consider splitting into its own package if end up being
a lot of routes.
"""
# Circular import OK here. See https://flask.palletsprojects.com/en/1.1.x/patterns/packages/
# pylint: disable=cyclic-import
from datetime import datetime
from flask import request
from elephant_vending_machine import APP
from .libraries.experiment_logger import create_experiment_logger

@APP.route('/run-trial', methods=['POST'])
def run_trial():
    """Responds with 'Running {trial_name}' string

    All requests sent to this route should have a trial_name in
    the query string, otherwise a 400 error will be returned

    Returns:
        HTTP response 200 with payload 'Running {trial_name}' or
        HTTP response 400 with payload 'No trial_name specified'
    """
    response = ""
    if request.args.get('trial_name') is not None:
        trial_name = request.args.get('trial_name')
        log_filename = str(datetime.utcnow()) + ' ' + trial_name + '.csv'
        exp_logger = create_experiment_logger(log_filename)

        exp_logger.info("Experiment %s started", trial_name)

        response = 'Running ' + str(trial_name)
    else:
        response = 'No trial_name specified'
    return response


@APP.route('/add-image', methods=['POST'])
def upload_image():
    """Responds with 'File received' string

    All requests sent to this route should have an image file
    included in the body of the request, otherwise a 400 error
    will be returned

    Returns:
        HTTP response 200 with payload 'File received' or
        HTTP response 500 with payload 'No image file in request.'
    """
    response = ""
    if 'file' in request.files:
        response = "File received."
    else:
        response = "No image file in request."
    return response

@APP.route('/log', methods=['GET'])
def log():
    """Returns the specified log file

    All requests sent to this route should have a log_name in
    the query string, otherwise a 400 error will be returned

    Returns:
        HTTP response 200 if log file exists, or HTTP response 500
        if it does not.
    """
    response = ""
    if request.args.get('log_name') is not None:
        response = 'This would be ' + request.args.get('log_name')
    else:
        response = 'Error with request.'
    return response
