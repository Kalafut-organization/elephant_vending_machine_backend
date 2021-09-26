"""Define all routes for the behavioral experiment server.

Here, all API routes for the experiment server are defined.
Consider splitting into its own package if end up being
a lot of routes.
"""

# Circular import OK here. See https://flask.palletsprojects.com/en/1.1.x/patterns/packages/
# pylint: disable=cyclic-import
from datetime import datetime
import importlib.util
import os
import subprocess
from subprocess import CalledProcessError
from flask import request, make_response, jsonify
from werkzeug.utils import secure_filename
from elephant_vending_machine import APP
from .libraries.experiment_logger import create_experiment_logger
from .libraries.vending_machine import VendingMachine

ALLOWED_IMG_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'svg'}
ALLOWED_EXPERIMENT_EXTENSIONS = {'py'}
IMAGE_UPLOAD_FOLDER = '/static/img'
EXPERIMENT_UPLOAD_FOLDER = '/static/experiment'
LOG_FOLDER = '/static/log'

@APP.route('/run-experiment/<filename>', methods=['POST'])
def run_experiment(filename):
    """Start execution of experiment python file specified by user

    **Example request**:

    .. sourcecode::

      POST /run-experiment?name=example_experiment HTTP/1.1
      Host: localhost:5000
      Accept-Encoding: gzip, deflate, br
      Content-Length:
      Connection: keep-alive

    **Example response**:

    .. sourcecode:: http

      HTTP/1.0 200 OK
      Content-Type: application/json; charset=utf-8
      Content-Length: 88
      Server: Werkzeug/0.16.1 Python/3.8.1
      Date: Thu, 13 Feb 2020 15:35:32 GMT

      {
        "log_file": "2020-03-17 05:15:06.558356 example_experiment.csv",
        "message": "Running example_experiment"
      }

    All requests sent to this route should have an experiment file
    included as a query parameter, otherwise a 400 error will be returned

    :status 200: experiment started
    :status 400: malformed request
    """
    path_to_current_file = os.path.dirname(os.path.abspath(__file__))
    experiment_directory = os.path.join(path_to_current_file, 'static', 'experiment')
    response_message = ""
    response_code = 400
    response_body = {}
    if filename in os.listdir(experiment_directory):
        log_filename = str(datetime.utcnow()) + ' ' + filename + '.csv'
        exp_logger = create_experiment_logger(log_filename)

        exp_logger.info('Experiment %s started', filename)

        spec = importlib.util.spec_from_file_location(
            filename,
            f'elephant_vending_machine/static/experiment/{filename}')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        vending_machine = VendingMachine(APP.config['REMOTE_HOSTS'], {})
        module.run_experiment(exp_logger, vending_machine)

        response_message = 'Running ' + str(filename)
        response_code = 200
        response_body['log_file'] = log_filename
    else:
        response_message = f"No experiment named {filename}"
        response_code = 400

    response_body['message'] = response_message
    return make_response(jsonify(response_body), response_code)

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
        ssh_command = f'''ssh -oStrictHostKeyChecking=accept-new -i /root/.ssh/id_rsa \
            {user}@{host} mkdir -p {directory}'''
        subprocess.run(ssh_command, check=True, shell=True)
        scp_command = f"scp {local_image_path}/{filename} {user}@{host}:{directory}/{filename}"
        subprocess.run(scp_command, check=True, shell=True)

def delete_remote_image(filename):
    """Deletes an image from the remote hosts defined in flask config.

    Parameters:
        filename (str): The filename of the remote file to be deleted

    Raises:
        CalledProcessError: If scp or ssh calls fail for one of the hosts
    """
    for host in APP.config['REMOTE_HOSTS']:
        user = APP.config['REMOTE_HOST_USERNAME']
        directory = APP.config['REMOTE_IMAGE_DIRECTORY']
        ssh_command = f'''ssh -oStrictHostKeyChecking=accept-new -i /root/.ssh/id_rsa \
            {user}@{host} rm {directory}/{filename}'''
        subprocess.run(ssh_command, check=True, shell=True)

def allowed_file(filename, allowed_extensions):
    """Determines whether an uploaded image file has an allowed extension.

    Parameters:
        filename (str): The filename which is to be checked
        allowed_extensions (array of str): The allowed file extensions

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

      {
          "message":"Success: Image saved."
      }

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
                if filename in os.listdir(save_path):
                    os.remove(os.path.join(save_path, filename))
                response = "Error: Failed to copy file to hosts. ", \
                  "Image not saved, please try again"
                response_code = 500
        else:
            response = "Error with request: File extension not allowed."
    return  make_response(jsonify({'message': response}), response_code)

@APP.route('/image/<filename>', methods=['DELETE'])
def delete_image(filename):
    """Returns a message indicating whether deletion of the specified file was successful

    **Example request**:

    .. sourcecode::

      DELETE /image/blank.jpg HTTP/1.1
      Host: 127.0.0.1
      Accept-Encoding: gzip, deflate, br
      Connection: keep-alive

    **Example response**:

    .. sourcecode:: http

      HTTP/1.0 200 OK
      Content-Type: application/json
      Content-Length: 59
      Access-Control-Allow-Origin: *
      Server: Werkzeug/0.16.1 Python/3.8.2
      Date: Fri, 27 Mar 2020 16:13:42 GMT

      {
        "message": "File blank.jpg was successfully deleted."
      }

    :status 200: image file successfully deleted
    :status 400: file with specified name could not be found
    """
    image_directory = os.path.dirname(os.path.abspath(__file__)) + IMAGE_UPLOAD_FOLDER
    response_code = 400
    response = ""
    if filename in os.listdir(image_directory):
        try:
            os.remove(os.path.join(image_directory, filename))
            delete_remote_image(filename)
            response = f"File {filename} was successfully deleted."
            response_code = 200
        except IsADirectoryError:
            response = f"{filename} exists, but is a directory and not a file. Deletion failed."
    else:
        response = f"File {filename} does not exist and so couldn't be deleted."
    return make_response(jsonify({'message': response}), response_code)

@APP.route('/image', methods=['GET'])
def list_images():
    """Returns a list of images from the images directory

    **Example request**:

    .. sourcecode::

      GET /image HTTP/1.1
      Host: 127.0.0.1
      Accept-Encoding: gzip, deflate, br
      Connection: keep-alive

    **Example response**:

    .. sourcecode:: http

      HTTP/1.0 200 OK
      Content-Type: application/json; charset=utf-8
      Content-Length: 212
      Server: Werkzeug/0.16.1 Python/3.8.1
      Date: Thu, 13 Feb 2020 15:35:32 GMT

      {
        "files": [
          "http://localhost/static/img/allBlack.png",
          "http://localhost/static/img/whiteStimuli.png"
        ]
      }

    :status 200: image file list successfully returned
    """
    resource_route = "/static/img/"
    file_request_path = request.base_url[:request.base_url.rfind('/')] + resource_route
    path_to_current_file = os.path.dirname(os.path.abspath(__file__))
    images_path = os.path.join(path_to_current_file, 'static', 'img')
    directory_list = os.listdir(images_path)
    image_files = [f for f in directory_list if os.path.isfile(os.path.join(images_path, f))]
    image_files.sort()
    if '.gitignore' in image_files:
        image_files.remove('.gitignore')
    full_image_paths = [file_request_path + f for f in image_files]
    response_code = 200
    return make_response(jsonify({'files': full_image_paths}), response_code)

@APP.route('/experiment', methods=['POST'])
def upload_experiment():
    """Return JSON body with message indicating result of experiment upload request

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

      {
          "message":"Success: Experiment saved."
      }

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
    return  make_response(jsonify({'message': response}), response_code)

@APP.route('/experiment/<filename>', methods=['DELETE'])
def delete_experiment(filename):
    """Returns a message indicating whether deletion of the specified file was successful

    **Example request**:

    .. sourcecode::

      DELETE /experiment/empty.py HTTP/1.1
      Host: 127.0.0.1
      Accept-Encoding: gzip, deflate, br
      Connection: keep-alive

    **Example response**:

    .. sourcecode:: http

      HTTP/1.0 200 OK
      Content-Type: application/json
      Content-Length: 59
      Access-Control-Allow-Origin: *
      Server: Werkzeug/0.16.1 Python/3.8.2
      Date: Fri, 27 Mar 2020 16:13:42 GMT

      {
        "message": "File empty.py was successfully deleted."
      }

    :status 200: experiment file successfully deleted
    :status 400: file with specified name could not be found
    """
    experiment_directory = os.path.dirname(os.path.abspath(__file__)) + EXPERIMENT_UPLOAD_FOLDER
    response_code = 400
    response = ""
    if filename in os.listdir(experiment_directory):
        try:
            os.remove(os.path.join(experiment_directory, filename))
            response = f"File {filename} was successfully deleted."
            response_code = 200
        except IsADirectoryError:
            response = f"{filename} exists, but is a directory and not a file. Deletion failed."
    else:
        response = f"File {filename} does not exist and so couldn't be deleted."
    return make_response(jsonify({'message': response}), response_code)

@APP.route('/experiment', methods=['GET'])
def list_experiments():
    """Returns a list of experiments from the experiment directory

    **Example request**:

    .. sourcecode::

      GET /experiment HTTP/1.1
      Host: 127.0.0.1
      Accept-Encoding: gzip, deflate, br
      Connection: keep-alive

    **Example response**:

    .. sourcecode:: http

      HTTP/1.0 200 OK
      Content-Type: application/json; charset=utf-8
      Content-Length: 212
      Server: Werkzeug/0.16.1 Python/3.8.1
      Date: Thu, 13 Feb 2020 15:35:32 GMT

      {
        "files": [
          "http://localhost/static/experiment/exampleExperiment.py",
          "http://localhost/static/experiment/testColorPerception.py"
        ]
      }

    :status 200: experiment file list successfully returned
    """
    resource_route = "/static/experiment/"
    file_request_path = request.base_url[:request.base_url.rfind('/')] + resource_route
    path_to_current_file = os.path.dirname(os.path.abspath(__file__))
    experiments_path = os.path.join(path_to_current_file, 'static', 'experiment')
    directory_list = os.listdir(experiments_path)
    exper_files = [f for f in directory_list if os.path.isfile(os.path.join(experiments_path, f))]
    exper_files.sort()
    if '.gitignore' in exper_files:
        exper_files.remove('.gitignore')
    full_experiment_paths = [file_request_path + f for f in exper_files]
    response_code = 200
    return make_response(jsonify({'files': full_experiment_paths}), response_code)

@APP.route('/log/<filename>', methods=['DELETE'])
def delete_log(filename):
    """Returns a message indicating whether deletion of the specified file was successful

    **Example request**:

    .. sourcecode::

      DELETE /log/somelog.csv HTTP/1.1
      Host: 127.0.0.1
      Accept-Encoding: gzip, deflate, br
      Connection: keep-alive

    **Example response**:

    .. sourcecode:: http

      HTTP/1.0 200 OK
      Content-Type: application/json
      Content-Length: 59
      Access-Control-Allow-Origin: *
      Server: Werkzeug/0.16.1 Python/3.8.2
      Date: Fri, 27 Mar 2020 16:13:42 GMT

      {
        "message": "File somelog.csv was successfully deleted."
      }

    :status 200: log file successfully deleted
    :status 400: file with specified name could not be found
    """
    log_directory = os.path.dirname(os.path.abspath(__file__)) + LOG_FOLDER
    response_code = 400
    response = ""
    if filename in os.listdir(log_directory):
        try:
            os.remove(os.path.join(log_directory, filename))
            response = f"File {filename} was successfully deleted."
            response_code = 200
        except IsADirectoryError:
            response = f"{filename} exists, but is a directory and not a file. Deletion failed."
    else:
        response = f"File {filename} does not exist and so couldn't be deleted."
    return make_response(jsonify({'message': response}), response_code)

@APP.route('/log', methods=['GET'])
def list_logs():
    """Returns a list of log resources from the log directory.

    **Example request**:

    .. sourcecode::

      GET /log HTTP/1.1
      Host: 127.0.0.1
      Accept-Encoding: gzip, deflate, br
      Connection: keep-alive

    **Example response**:

    .. sourcecode:: http

      HTTP/1.0 200 OK
      Content-Type: application/json; charset=utf-8
      Content-Length: 212
      Server: Werkzeug/0.16.1 Python/3.8.1
      Date: Thu, 13 Feb 2020 15:35:32 GMT

      {
        "files": [
          "http://localhost:5000/static/log/2020-03-17 04:26:02.085651 exampleExperiment.csv",
          "http://localhost:5000/static/log/2020-03-17 04:27:04.019992 exampleExperiment.csv"
        ]
      }

    :status 200: log file list successfully returned
    """
    resource_route = "/static/log/"
    file_request_path = request.base_url[:request.base_url.rfind('/')] + resource_route
    path_to_current_file = os.path.dirname(os.path.abspath(__file__))
    logs_path = os.path.join(path_to_current_file, 'static', 'log')
    directory_list = os.listdir(logs_path)
    log_files = [f for f in directory_list if os.path.isfile(os.path.join(logs_path, f))]
    log_files.sort()
    if '.gitignore' in log_files:
        log_files.remove('.gitignore')
    full_log_paths = [file_request_path + f for f in log_files]
    response_code = 200
    return make_response(jsonify({'files': full_log_paths}), response_code)
