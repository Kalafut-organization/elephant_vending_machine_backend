import pytest

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

def test_run_trial_route_success(client, monkeypatch):
    monkeypatch.setattr('elephant_vending_machine.views.create_experiment_logger', lambda file_name: MockLogger())
    response = client.post('/run-trial?trial_name=demo')
    assert b'Running demo' in response.data

def test_run_trial_route_empty_query_string(client):
    response = client.post('/run-trial')
    assert b'No trial_name specified' in response.data

def test_get_log_route_success(client):
    response = client.get('/log?log_name=alog')
    assert b'This would be alog' in response.data

def test_get_log_route_no_log_name(client):
    response = client.get('/log')
    assert b'Error with request.' in response.data
