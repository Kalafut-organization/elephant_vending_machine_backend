"""Define all routes for the behavioral experiment server.

Here, all API routes for the experiment server are defined.
Consider splitting into its own package if end up being
a lot of routes.
"""

# Circular import OK here. See https://flask.palletsprojects.com/en/1.1.x/patterns/packages/
# pylint: disable=cyclic-import
# pylint: disable=W0603
from datetime import datetime
import importlib.util
import os
import sys
import shutil
import subprocess
from subprocess import CalledProcessError
import py_compile
from flask import json, request, make_response, jsonify
from werkzeug.utils import secure_filename
from elephant_vending_machine import APP
from .libraries.experiment_logger import create_experiment_logger
from .libraries.vending_machine import VendingMachine

ALLOWED_IMG_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'svg'}
ALLOWED_EXPERIMENT_EXTENSIONS = {'py'}
IMAGE_UPLOAD_FOLDER = '/static/img'
EXPERIMENT_UPLOAD_FOLDER = '/static/experiment'
LOG_FOLDER = '/static/log'
VENDING_MACHINE_OBJ = None

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
        global VENDING_MACHINE_OBJ
        VENDING_MACHINE_OBJ = vending_machine
        module.run_experiment(exp_logger, vending_machine)

        response_message = 'Running ' + str(filename)
        response_code = 200
        response_body['log_file'] = log_filename
    else:
        response_message = f"No experiment named {filename}"
        response_code = 400

    response_body['message'] = response_message
    return make_response(jsonify(response_body), response_code)

@APP.route('/signal', methods=['POST'])
def get_signal():
    """Receives a signal from monitor pi, and sets the vending machine's signal_sender variable
    """
    response_message = ""
    response_code = 400
    response_body = {}
    if VENDING_MACHINE_OBJ:
        VENDING_MACHINE_OBJ.signal_sender = request.form['address']
        response_code = 200
        response_body = {}
        response_message = "Success: Signal sent"
    else:
        response_message = "Error: There is currently no running experiment"
    response_body['message'] = response_message
    return make_response(jsonify(response_body), response_code)

def add_remote_image(local_image_path, group, filename):
    """Adds an image to the remote hosts defined in flask config.

    Parameters:
        local_image_path (str): The local path of the image to be copied
        filename (str): The filename of the local file to be copied

    Raises:
        CalledProcessError: If scp or ssh calls fail for one of the hosts
    """
    for host in APP.config['REMOTE_HOSTS']:
        user = APP.config['REMOTE_HOST_USERNAME']
        directory = APP.config['REMOTE_IMAGE_DIRECTORY'] + '/' + group
        ssh_command = f'''ssh -oStrictHostKeyChecking=accept-new -i /root/.ssh/id_rsa \
            {user}@{host} mkdir -p {directory}'''
        subprocess.run(ssh_command, check=True, shell=True)
        scp_command = f"scp {local_image_path}/{filename} {user}@{host}:{directory}/{filename}"
        subprocess.run(scp_command, check=True, shell=True)

def delete_remote_image(group, filename):
    """Deletes an image from the remote hosts defined in flask config.

    Parameters:
        filename (str): The filename of the remote file to be deleted

    Raises:
        CalledProcessError: If scp or ssh calls fail for one of the hosts
    """
    for host in APP.config['REMOTE_HOSTS']:
        user = APP.config['REMOTE_HOST_USERNAME']
        directory = APP.config['REMOTE_IMAGE_DIRECTORY'] + '/' + group
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


@APP.route('/<group>/image', methods=['POST'])
def upload_image(group):
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
            save_path = os.path.dirname(os.path.abspath(__file__)) \
               + IMAGE_UPLOAD_FOLDER + "/" + group
            file.save(os.path.join(save_path, filename))
            response = "Success: Image saved."
            response_code = 201

            try:
                add_remote_image(save_path, group, filename)
            except CalledProcessError:
                if filename in os.listdir(save_path):
                    os.remove(os.path.join(save_path, filename))
                response = "Error: Failed to copy file to hosts. ", \
                  "Image not saved, please try again"
                response_code = 500
        else:
            response = "Error with request: File extension not allowed."
    return  make_response(jsonify({'message': response}), response_code)

@APP.route('/<group>/<image>/copy', methods=['POST'])
def copy_image(group, image):
    """Returns a message indicating whether copying of the specified file was successful

    **Example request**:

    .. sourcecode::

      POST /test1/blank.jpg/copy HTTP/1.1
      Host: 127.0.0.1
      Content-Type: multipart/form-data; boundary=--------------------------827430006917349763475527
      Accept-Encoding: gzip, deflate, br
      Content-Length: 737067
      Connection: keep-alive
      ----------------------------827430006917349763475527
      Content-Disposition: form-data; name="test2"

      {name: "test2"}
      ----------------------------827430006917349763475527--

    **Example response**:

    .. sourcecode:: http

      HTTP/1.0 200 OK
      Content-Type: application/json
      Content-Length: 59
      Access-Control-Allow-Origin: *
      Server: Werkzeug/0.16.1 Python/3.8.2
      Date: Fri, 27 Mar 2020 16:13:42 GMT

      {
        "message": "File blank.jpg was successfully copied to group 'test2'."
      }

    :status 200: image file successfully copied
    :status 400: group with specified name could not be found
    """
    response = ""
    response_code = 400
    group2 = request.form["name"]
    old_group = image_path = os.path.dirname(os.path.abspath(__file__)) + \
      IMAGE_UPLOAD_FOLDER + "/" + group
    image_path = os.path.dirname(os.path.abspath(__file__)) + \
      IMAGE_UPLOAD_FOLDER + "/" + group + "/" + image
    group_path = os.path.dirname(os.path.abspath(__file__)) + IMAGE_UPLOAD_FOLDER + "/" + group2
    print(image_path, file=sys.stderr)
    if os.path.isdir(group_path):
        if os.path.exists(image_path):
            try:
                add_remote_image(old_group, group2, image)
                shutil.copy(image_path, group_path)
                response = "File " + image + " was successfully copied to group '" + 	group2 + "'."
                response_code = 200
            except CalledProcessError:
                if os.path.exists(group_path + "/" + image):
                    os.remove(group_path + "/" + image)
                response = "Error: Failed to copy file to hosts. ", \
                  "Image not copied, please try again"
                response_code = 500
        else:
            response = "Error with request: " + image + " does not exist"
    else:
        response = "Error with request: " + group2 + " is not an existing directory"
    return  make_response(jsonify({'message': response}), response_code)

@APP.route('/image/<group>/<filename>', methods=['DELETE'])
def delete_image(group, filename):
    """Returns a message indicating whether deletion of the specified file was successful

    **Example request**:

    .. sourcecode::

      DELETE /image/group-name/blank.jpg HTTP/1.1
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
    response_code = 400
    response = ""
    image_directory = os.path.dirname(os.path.abspath(__file__)) + IMAGE_UPLOAD_FOLDER + "/" + group
    if os.path.isdir(image_directory):
        if filename in os.listdir(image_directory):
            try:
                try:
                    delete_remote_image(group, filename)
                    os.remove(os.path.join(image_directory, filename))
                    response = f"File {filename} was successfully deleted."
                    response_code = 200
                except CalledProcessError:
                    response_code = 500
                    response = "Error: Failed to delete file from hosts. ", \
                    "Image not deleted, please try again"
            except IsADirectoryError:
                response = f"{filename} exists, but is a directory and not a file. Deletion failed."
        else:
            response = f"File {filename} does not exist and so couldn't be deleted."
    else:
        response = f"Group {group} does not exist"
    return make_response(jsonify({'message': response}), response_code)

@APP.route('/<group>', methods=['GET'])
def list_images(group):
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
    resource_route = "/static/img/" + group + "/"
    file_request_path = request.base_url[:request.base_url.rfind('/')] + resource_route
    path_to_current_file = os.path.dirname(os.path.abspath(__file__))
    images_path = os.path.join(path_to_current_file, 'static', 'img', group)
    directory_list = os.listdir(images_path)
    image_files = [f for f in directory_list if os.path.isfile(os.path.join(images_path, f))]
    image_files.sort()
    if '.gitignore' in image_files:
        image_files.remove('.gitignore')
    full_image_paths = [file_request_path + f for f in image_files]
    response_code = 200
    return make_response(jsonify({'files': full_image_paths}), response_code)

def allowed_experiment(name):
    """Determines whether a group exists in the directory already"""
    directory = os.path.dirname(os.path.abspath(__file__)) + EXPERIMENT_UPLOAD_FOLDER
    expr = os.listdir(directory)
    return name not in expr

@APP.route('/experiment/create', methods=['POST'])
def create_experiment_from_form():
    """Return JSON body with message indicating result of group creation request"""
    response = ""
    response_code = 400
    #pull template file
    print(request.form)
    with open(os.path.dirname(os.path.abspath(__file__))+\
    '/static/templates/form_template.py', \
    'r') as file:
        filedata = file.read()

    # #Replace variables with form data
    filedata = filedata.replace("_inter_fix_duration", request.form['intermediate_duration'])
    filedata = filedata.replace("_fixation_duration", \
    request.form['fixation_duration']) # ^ watch the order with these two
    filedata = filedata.replace("_stimuli_duration", request.form['stimuli_duration'])
    filedata = filedata.replace("_num_trials", request.form['trials'])
    filedata = filedata.replace("_replacement", request.form['replacement'].capitalize())
    filedata = filedata.replace("_monitor_count", request.form['monitors'])
    # filedata = filedata.replace("_intertrial_interval", request.form['trial_interval'])
    # find the correct fixation
    fixation = ""
    if request.form['fixation_default']:
        fixation = "\'fixation_stimuli.png\'"
    else:
        fixation = request.form['new_fixation']
    filedata = filedata.replace("_fixation_stimuli", fixation)
    #preconfigure string with array for groups
    outcomes = request.form['outcomes']
    outcome_list = json.loads(outcomes)
    for item in outcome_list:
        print(item)
        item[0] = "/home/pi/elephant_vending_machine_backend/elephant_vending_machine/static/img/" \
         + item[0]
    outcomes = json.dumps(outcome_list)
    stim_groups = "STIMULI_GROUPS = " + outcomes
    filedata = filedata.replace("STIMULI_GROUPS = []", stim_groups)

    #save new experiment file in experiments and overwite
    name = request.form['name']
    if allowed_experiment(name):
        response_code = 200
        response = "File successfully created."
        filepath = ( \
            "elephant_vending_machine/static/experiment/" \
            + name + ".py")
        with open(filepath, 'w') as file:
            file.write(filedata)
    else:
        response = "Error with request: File extension not allowed."
    return make_response(jsonify({'message':response}), response_code)

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
            try:
                py_compile.compile(os.path.join(save_path, filename), doraise=True)
            except py_compile.PyCompileError:
                os.remove(os.path.join(save_path, filename))
                response = "Error: Experiment failed to compile correctly,", \
                   "please fix the errors and re-upload"
                response_code = 400
                return  make_response(jsonify({'message': response}), response_code)
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

def allowed_group(name):
    """Determines whether a group exists in the directory already"""
    directory = os.path.dirname(os.path.abspath(__file__)) + IMAGE_UPLOAD_FOLDER
    groups = os.listdir(directory)
    return name not in groups

def add_remote_group(group_name):
    """Adds a group to the remote hosts defined in flask config.

    Parameters:
        group_name (str): The filename of the local group to be copied

    Raises:
        CalledProcessError: If scp or ssh calls fail for one of the hosts
    """
    for host in APP.config['REMOTE_HOSTS']:
        user = APP.config['REMOTE_HOST_USERNAME']
        directory = APP.config['REMOTE_IMAGE_DIRECTORY']
        ssh_command = f'''ssh -oStrictHostKeyChecking=accept-new -i /root/.ssh/id_rsa \
            {user}@{host} mkdir -p {directory}'''
        subprocess.run(ssh_command, check=True, shell=True)
        mkdir_command = f'''ssh -oStrictHostKeyChecking=accept-new -i /root/.ssh/id_rsa \
            {user}@{host} mkdir -p {directory}/{group_name}'''
        subprocess.run(mkdir_command, check=True, shell=True)

def delete_remote_group(group_name):
    """Deletes a group from the remote hosts defined in flask config.

    Parameters:
        group_name (str): The name of the remote group to be deleted

    Raises:
        CalledProcessError: If scp or ssh calls fail for one of the hosts
    """
    for host in APP.config['REMOTE_HOSTS']:
        user = APP.config['REMOTE_HOST_USERNAME']
        directory = APP.config['REMOTE_IMAGE_DIRECTORY']
        ssh_command = f'''ssh -oStrictHostKeyChecking=accept-new -i /root/.ssh/id_rsa \
            {user}@{host} rm -r {directory}/{group_name}'''
        subprocess.run(ssh_command, check=True, shell=True)

@APP.route('/groups', methods=['GET'])
def list_groups():
    """Return JSON body with message of all folders in the static/img directory"""
    path_to_current_file = os.path.dirname(os.path.abspath(__file__))
    images_path = os.path.join(path_to_current_file, 'static', 'img')
    groups = os.listdir(images_path)
    groups.sort()
    if '.gitignore' in groups:
        groups.remove('.gitignore')
    for group in groups:
        if not os.path.isdir(os.path.join(images_path, group)):
            groups.remove(group)
    response_code = 200
    return make_response(jsonify({'names': groups}), response_code)

@APP.route('/groups', methods=['POST'])
def create_group():
    """Return JSON body with message indicating result of group creation request"""
    response = ""
    response_code = 400
    if 'name' not in request.form:
        response = "Error with request: No name field in body of request."
    else:
        group_name = request.form['name']
        if group_name == '':
            response = "Error with request: Group name must not be empty."
        elif allowed_group(group_name):
            filename = secure_filename(group_name)
            try:
                add_remote_group(filename)
                save_path = os.path.dirname(os.path.abspath(__file__))+IMAGE_UPLOAD_FOLDER
                folder = os.path.join(save_path, filename)
                os.makedirs(folder)
                response = "Success: Group created."
                response_code = 201
            except CalledProcessError:
                response = "Error: Failed to create group on hosts."
                response_code = 500
        else:
            response = "Error with request: Group already exists."
    return make_response(jsonify({'message': response}), response_code)


@APP.route('/groups/<name>', methods=['DELETE'])
def delete_group(name):
    """Return JSON body with message indicating result of group deletion request"""
    directory = os.path.dirname(os.path.abspath(__file__)) + IMAGE_UPLOAD_FOLDER
    response_code = 400
    response = ""
    if name in os.listdir(directory):
        try:
            shutil.rmtree(os.path.join(directory, name))
            delete_remote_group(name)
            response = f"Group {name} was successfully deleted."
            response_code = 200
        except OSError:
            response = "An error has occurred and the group could not be deleted"
    else:
        response = f"Group {name} does not exist and so couldn't be deleted."
    return make_response(jsonify({'message': response}), response_code)

@APP.route('/template', methods=['GET'])
def download_example_path(filename="form_template.py"):
    """Return file to be downloaded"""
    resource_route = "/static/templates/"
    file_request_path = request.base_url[:request.base_url.rfind('/')] + resource_route
    sample_path = file_request_path + filename
    response_code = 200
    return make_response(jsonify({'files': [sample_path]}), response_code)
