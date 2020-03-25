import pytest
import os
import subprocess
from flask import jsonify, make_response
import json

from elephant_vending_machine import elephant_vending_machine

class MockLogger:

    @staticmethod
    def info(*args, **kwargs):
        return 

@pytest.fixture
def client():
    elephant_vending_machine.APP.config['TESTING'] = True

    with elephant_vending_machine.APP.test_client() as client:
        yield client
        subprocess.call(["rm","elephant_vending_machine/static/logs/test_file.csv"])
        subprocess.call(["rm","elephant_vending_machine/static/logs/test_file2.csv"])
        subprocess.call(["rm", "elephant_vending_machine/static/img/test_file.png"])
        subprocess.call(["rm", "elephant_vending_machine/static/img/test_file2.jpg"])

def test_run_trial_route_success(client, monkeypatch):
    monkeypatch.setattr('elephant_vending_machine.views.create_experiment_logger', lambda file_name: MockLogger())
    response = client.post('/run-trial?trial_name=demo')
    assert b'Running demo' in response.data
    assert response.status_code == 200

def test_run_trial_route_empty_query_string(client):
    response = client.post('/run-trial')
    assert b'No trial_name specified' in response.data
    assert response.status_code == 400

def test_get_log_endpoint(client):
    subprocess.call(["touch", "elephant_vending_machine/static/logs/test_file.csv"])
    subprocess.call(["touch", "elephant_vending_machine/static/logs/test_file2.csv"])
    response = client.get('/log')
    response_json_files = json.loads(response.data)['files']
    min_elements_expected = ["http://localhost/static/logs/test_file.csv","http://localhost/static/logs/test_file2.csv","http://localhost/static/logs/unittest.csv"]
    assert all(elem in response_json_files for elem in min_elements_expected)
    assert response.status_code == 200

def test_get_image_endpoint(client):
    subprocess.call(["touch", "elephant_vending_machine/static/img/test_file.png"])
    subprocess.call(["touch", "elephant_vending_machine/static/img/test_file2.jpg"])
    response = client.get('/image')
    response_json_files = json.loads(response.data)['files']
    min_elements_expected = ["http://localhost/static/img/test_file.png","http://localhost/static/img/test_file2.jpg"]
    assert all(elem in response_json_files for elem in min_elements_expected)
    assert response.status_code == 200
