import py_compile
import pytest
import os
import subprocess
from flask import jsonify, make_response
from io import BytesIO
import json

from elephant_vending_machine import elephant_vending_machine
from elephant_vending_machine import views
from subprocess import CompletedProcess, CalledProcessError

def raise_(ex):
    raise ex

@pytest.fixture
def client():
    elephant_vending_machine.APP.config['TESTING'] = True

    with elephant_vending_machine.APP.test_client() as client:
        yield client
        subprocess.call(["rm","elephant_vending_machine/static/experiment/test_file.py"])
        subprocess.call(["rm","elephant_vending_machine/static/experiment/test_file2.py"])
        subprocess.call(["rm","elephant_vending_machine/static/experiment/empty.py"])

def test_post_experiment_route_no_file(client):
    response = client.post('/experiment')
    assert response.status_code == 400
    assert b'Error with request: No file field in body of request.' in response.data

def test_post_experiment_route_empty_filename(client):
    data = {'file': (BytesIO(b"Testing: \x00\x01"), '')}
    response = client.post('/experiment', data=data) 
    assert response.status_code == 400
    assert b'Error with request: File field in body of response with no file present.' in response.data

def test_post_experiment_route_with_file_bad_extension(client):
    data = {'file': (BytesIO(b"Testing: \x00\x01"), 'test_file.sh')}
    response = client.post('/experiment', data=data) 
    assert response.status_code == 400
    assert b'Error with request: File extension not allowed.' in response.data

def test_post_experiment_route_with_file(monkeypatch, client):
    monkeypatch.setattr('werkzeug.datastructures.FileStorage.save', lambda save_path, filename: "" )
    subprocess.call(["touch", "elephant_vending_machine/static/experiment/test_file.py"])
    data = {'file': (BytesIO(b"Testing: \x00\x01"), 'test_file.py')}
    response = client.post('/experiment', data=data) 
    assert response.status_code == 201
    assert b'Success: Experiment saved.' in response.data

def test_post_experiment_route_compiler_error(monkeypatch, client):
    subprocess.call(["touch", "elephant_vending_machine/static/experiment/test_file.py"])
    data = {'file': (BytesIO(b"Testing: \x00\x01"), 'test_file.py')}
    response = client.post('/experiment', data=data) 
    assert response.status_code == 400
    assert b'Error: Experiment failed to compile correctly,', \
         'please fix the errors and re-upload' in response.data

def test_get_experiemnt_list_all_endpoint(client):
    subprocess.call(["touch", "elephant_vending_machine/static/experiment/test_file.py"])
    subprocess.call(["touch", "elephant_vending_machine/static/experiment/test_file2.py"])
    response = client.get('/experiment')
    response_json_files = json.loads(response.data)['files']
    min_elements_expected = ["http://localhost/static/experiment/test_file.py","http://localhost/static/experiment/test_file2.py"]
    assert all(elem in response_json_files for elem in min_elements_expected)
    assert response.status_code == 200

def test_delete_experiment_happy_path(client):
    subprocess.call(["touch", "elephant_vending_machine/static/experiment/empty.py"])
    response = client.delete('/experiment/empty.py')
    assert response.status_code == 200
    assert json.loads(response.data)['message'] == 'File empty.py was successfully deleted.'

def test_delete_experiment_file_not_found(client):
    response = client.delete('/experiment/empty.py')
    assert response.status_code == 400
    assert json.loads(response.data)['message'] == 'File empty.py does not exist and so couldn\'t be deleted.'

def test_delete_experiment_is_a_directory_exception(client, monkeypatch):
    subprocess.call(["touch", "elephant_vending_machine/static/experiment/empty.py"])
    monkeypatch.setattr('os.remove', lambda file: (_ for _ in ()).throw(IsADirectoryError))
    response = client.delete('/experiment/empty.py')
    assert response.status_code == 400
    assert json.loads(response.data)['message'] == 'empty.py exists, but is a directory and not a file. Deletion failed.'

def test_valid_file_extensions_valid_file():
    assert views.allowed_file('pythonscript.py', {'py'}) == True

def test_valid_file_extensions_invalid_file():
    assert views.allowed_file('sourcecode.c', {'py'}) == False

def test_valid_file_extension_double_extension():
    assert views.allowed_file('sourcecode.c.py', {'py'}) == True

def test_experiment_template(client):
    subprocess.call(["touch", "elephant_vending_machine/static/experiment/test_file.py"])
    subprocess.call(["touch", "elephant_vending_machine/static/experiment/test_file2.py"])
    subprocess.call(["touch", "elephant_vending_machine/static/experiment/empty.py"])
    response = client.get('/template')
    response_json_files = json.loads(response.data)['files']
    assert response_json_files == ["http://localhost/static/templates/form_template.py"]

def test_template_creation(client):
    subprocess.call(["touch", "elephant_vending_machine/static/experiment/test_file.py"])
    subprocess.call(["touch", "elephant_vending_machine/static/experiment/test_file2.py"])
    subprocess.call(["touch", "elephant_vending_machine/static/experiment/empty.py"])
    data = {'name': "name", 'intermediate_duration': 5, 'intertrial_duration': 5, 'stimuli_duration': 5, 'fixation_duration': 5, 'fixation_default': True, 'trials':2, 'replacement': "False", "monitors":'[true, false, true]', "fixation":"", "outcomes":'[["group1","treat1","tray1"]]'}
    response = client.post('/experiment/create', data=data) 
    assert response.status_code == 200
    assert json.loads(response.data)['message'] == "File successfully created."