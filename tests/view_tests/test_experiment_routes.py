import pytest
import os
import subprocess
from flask import jsonify, make_response
from io import BytesIO

from elephant_vending_machine import elephant_vending_machine
from subprocess import CompletedProcess, CalledProcessError

def raise_(ex):
    raise ex

@pytest.fixture
def client():
    elephant_vending_machine.APP.config['TESTING'] = True

    with elephant_vending_machine.APP.test_client() as client:
        yield client
        subprocess.call(["rm","elephant_vending_machine/static/experiments/test_file.py"])
        subprocess.call(["rm","elephant_vending_machine/static/experiments/test_file2.py"])

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
    data = {'file': (BytesIO(b"Testing: \x00\x01"), 'test_file.py')}
    response = client.post('/experiment', data=data) 
    assert response.status_code == 201
    assert b'Success: Experiment saved.' in response.data

def test_get_experiemnt_list_all_endpoint(client):
    path_to_current_file = os.path.dirname(os.path.abspath(__file__))
    save_path = os.path.join(path_to_current_file, '..','..','elephant_vending_machine','static','experiments')
    subprocess.call(["touch", "elephant_vending_machine/static/experiments/test_file.py"])
    subprocess.call(["touch", "elephant_vending_machine/static/experiments/test_file2.py"])
    response = client.get('/experiment')
    assert make_response(jsonify({'files': ["http://localhost/experiment/test_file.py","http://localhost/experiment/test_file2.py"]})).data in response.data
    assert response.status_code == 200
