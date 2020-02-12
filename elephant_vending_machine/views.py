"""Define all routes for the behavioral experiment server.

Here, all API routes for the experiment server are defined.
Consider splitting into its own package if end up being
a lot of routes.
"""

# Circular import OK here. See https://flask.palletsprojects.com/en/1.1.x/patterns/packages/
# pylint: disable=cyclic-import
from datetime import datetime
import os
from flask import request
from werkzeug.utils import secure_filename
from elephant_vending_machine import APP
from .libraries.experiment_logger import create_experiment_logger

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'svg'}

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


@APP.route('/image', methods=['POST'])
def upload_image():
    """Responds with 'File received' string

    All requests sent to this route should have an image file
    included in the body of the request, otherwise a 400 error
    will be returned

    Returns:
        HTTP response 200 with payload 'Success: Image saved.' or
        HTTP response 400 with payload describing the issue with the request.
    """

    response = ""
    response_code = 400
    if 'file' not in request.files:
        response = "Error with request: No file field in body of request."
    else:
        file = request.files['file']
        if file.filename == '':
            response = "Error with request: File field in body of response with no file present."
        elif file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(APP.config['IMAGE_UPLOAD_FOLDER'], filename))
            response = "Success: Image saved."
            response_code = 200
        else:
            response = "Error with request: File extension not allowed."
    return response, response_code

def allowed_file(filename):
    """Determines whether an uploaded image file has an allowed extension.

    Returns:
        True if filename includes extension and extension is an allowed extension
        False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
