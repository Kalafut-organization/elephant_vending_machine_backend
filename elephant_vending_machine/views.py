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

def allowed_file(filename):
    """Determines whether an uploaded image file has an allowed extension.

    Returns:
        True if filename includes extension and extension is an allowed extension
        False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@APP.route('/image', methods=['POST'])
def upload_image():
    """Return string indicating result of request

    **Example request**:

    .. sourcecode:: http
      
      POST /image HTTP/1.1
      Host: 127.0.0.1:5000
      Content-Type: multipart/form-data; boundary=--------------------------827430006917349763475527
      Accept-Encoding: gzip, deflate, br
      Content-Length: 737067
      Connection: keep-alive
      ----------------------------827430006917349763475527
      Content-Disposition: form-data; name="file"; filename="elephant.jpeg"

      <elephant.jpeg>
      ----------------------------827430006917349763475527--

    **Example response**:

    .. sourcecode:: http

      HTTP/1.0 200 OK
      Content-Type: text/html; charset=utf-8
      Content-Length: 21
      Server: Werkzeug/0.16.1 Python/3.8.1
      Date: Thu, 13 Feb 2020 15:35:32 GMT

      Success: Image saved.

    All requests sent to this route should have an image file
    included in the body of the request, otherwise a 400 error
    will be returned

    :status 200: file saved
    :status 400: malformed request
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
