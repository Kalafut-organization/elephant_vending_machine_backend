import pytest
import os
import subprocess

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
        subprocess.call(["rm","logs/test_file.csv"])
        subprocess.call(["rm","logs/test_file2.csv"])

def test_run_trial_route_success(client, monkeypatch):
    monkeypatch.setattr('elephant_vending_machine.views.create_experiment_logger', lambda file_name: MockLogger())
    response = client.post('/run-trial?trial_name=demo')
    assert b'Running demo' in response.data

def test_run_trial_route_empty_query_string(client):
    response = client.post('/run-trial')
    assert b'No trial_name specified' in response.data

def test_get_log_endpoint(client):
    path_to_current_file = os.path.dirname(os.path.abspath(__file__))
    save_path = os.path.join(path_to_current_file, '..','..','logs')
    subprocess.call(["touch", "logs/test_file.csv"])
    subprocess.call(["touch", "logs/test_file2.csv"])
    response = client.get('/log')
    assert b'test_file2.csv, unittest.csv, test_file.csv' in response.data
    assert response.status_code == 200
