"""Define all routes for the behavioral experiment server.

Here, all API routes for the experiment server are defined.
Consider splitting into its own package if end up being
a lot of routes.
"""

# Circular import OK here. See https://flask.palletsprojects.com/en/1.1.x/patterns/packages/
# pylint: disable=cyclic-import
from datetime import datetime
import os
import subprocess
from subprocess import CalledProcessError
from flask import request, make_response, jsonify
from werkzeug.utils import secure_filename
from elephant_vending_machine import APP
from .libraries.experiment_logger import create_experiment_logger

ALLOWED_IMG_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'svg'}
ALLOWED_EXPERIMENT_EXTENSIONS = {'py'}
IMAGE_UPLOAD_FOLDER = '/static/img'
EXPERIMENT_UPLOAD_FOLDER = '/static/experiments'

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

def add_remote_image(local_image_path, filename):
    """Adds an image to the remote hosts defined in flask config.

    Parameters:
        local_image_path (str): The local path of the image to be copied
        filename (str): The filename of the local file to be copied

    Raises:
        CalledProcessError: If scp or ssh calls fail for one of the hosts
    """
    for host in APP.config['REMOTE_HOSTS']:
        user = APP.config['REMOTE_HOST_USERNAME']
        directory = APP.config['REMOTE_IMAGE_DIRECTORY']
        ssh_command = f"ssh {user}@{host} mkdir -p {directory}"
        subprocess.run(ssh_command, check=True)
        scp_command = f"scp {local_image_path}/{filename} {user}@{host}:{directory}/{filename}"
        subprocess.run(scp_command, check=True)

def allowed_file(filename, allowed_extensions):
    """Determines whether an uploaded image file has an allowed extension.

    Parameters:
        filename (str): The filename which is to be checked

    Returns:
        True if filename includes extension and extension is an allowed extension
        False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


@APP.route('/image', methods=['POST'])
def upload_image():
    """Return string indicating result of image upload request

    **Example request**:

    .. sourcecode::

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

    :status 201: file saved
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
        elif file and allowed_file(file.filename, ALLOWED_IMG_EXTENSIONS):
            filename = secure_filename(file.filename)
            save_path = os.path.dirname(os.path.abspath(__file__)) + IMAGE_UPLOAD_FOLDER
            file.save(os.path.join(save_path, filename))
            response = "Success: Image saved."
            response_code = 201

            try:
                add_remote_image(save_path, filename)
            except CalledProcessError:
                response = "Error: Failed to copy file to hosts"
                response_code = 500
        else:
            response = "Error with request: File extension not allowed."
    return response, response_code

@APP.route('/experiment', methods=['POST'])
def upload_experiment():
    """Return string indicating result of experiemnt upload request

    **Example request**:

    .. sourcecode::

      POST /experiment HTTP/1.1
      Host: 127.0.0.1:5000
      Content-Type: multipart/form-data; boundary=--------------------------827430006917349763475527
      Accept-Encoding: gzip, deflate, br
      Content-Length: 737067
      Connection: keep-alive
      ----------------------------827430006917349763475527
      Content-Disposition: form-data; name="file"; filename="elephant.py"

      <elephant.py>
      ----------------------------827430006917349763475527--

    **Example response**:

    .. sourcecode:: http

      HTTP/1.0 200 OK
      Content-Type: text/html; charset=utf-8
      Content-Length: 21
      Server: Werkzeug/0.16.1 Python/3.8.1
      Date: Thu, 13 Feb 2020 15:35:32 GMT

      Success: Image saved.

    All requests sent to this route should have a python script file
    included in the body of the request, otherwise a 400 error
    will be returned

    :status 201: file saved
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
        elif file and allowed_file(file.filename, ALLOWED_EXPERIMENT_EXTENSIONS):
            filename = file.filename
            save_path = os.path.dirname(os.path.abspath(__file__)) + EXPERIMENT_UPLOAD_FOLDER
            file.save(os.path.join(save_path, filename))
            response = "Success: Experiment saved."
            response_code = 201
        else:
            response = "Error with request: File extension not allowed."
    return response, response_code

@APP.route('/log', methods=['GET'])
def list_logs():
    """Returns a list of experiment filenames from the experiments directory.

    Returns:
        HTTP response 200 with string containing comma-separated filenames.

    """
    path_to_current_file = os.path.dirname(os.path.abspath(__file__))
    logs_path = os.path.join(path_to_current_file, '..', 'logs')
    directory_list = os.listdir(logs_path)
    experiment_files = [f for f in directory_list if os.path.isfile(os.path.join(logs_path, f))]
    experiment_files.remove('.gitignore')
    response_code = 200
    return make_response(jsonify({'files': experiment_files}), response_code)
