import pytest
import subprocess
from io import BytesIO
import json

from werkzeug.wrappers import Response

from elephant_vending_machine import elephant_vending_machine
from subprocess import CompletedProcess, CalledProcessError

def raise_(ex):
    raise ex

@pytest.fixture
def client():
    elephant_vending_machine.APP.config['TESTING'] = True

    with elephant_vending_machine.APP.test_client() as client:
        yield client
        subprocess.call(["rmdir","elephant_vending_machine/static/img/test"])
        subprocess.call(["rmdir","elephant_vending_machine/static/img/test2"])

def test_post_group_route_no_name(client):
    response = client.post('/groups')
    assert response.status_code == 400
    assert b'Error with request: No name field in body of request.' in response.data

def test_post_group_route_empty_name(client):
    data = {'name': ''}
    response = client.post('/groups', data=data) 
    assert response.status_code == 400
    assert json.loads(response.data)['message'] == 'Error with request: Group name must not be empty.'

def test_post_group_route_duplicate(client):
    subprocess.call(["mkdir", "elephant_vending_machine/static/img/test"])
    data = {'name': 'test'}
    response = client.post('/groups', data=data)
    assert response.status_code == 400
    assert json.loads(response.data)['message'] == 'Error with request: Group already exists.'

def test_post_group_route_copying_exception(monkeypatch, client):
    monkeypatch.setattr('subprocess.run', lambda command, check, shell: raise_(CalledProcessError(1, ['ssh'])))
    data = {'name': 'test'}
    response = client.post('/groups', data=data)
    assert response.status_code == 500
    assert json.loads(response.data)['message'] == 'Error: Failed to create group on hosts.'

def test_post_group_route_happy_path(monkeypatch, client):
    monkeypatch.setattr('subprocess.run', lambda command, check, shell: CompletedProcess(['some_command'], returncode=0))
    data = {'name': 'test'}
    response = client.post('/groups', data=data)
    assert response.status_code == 201
    assert b'Success: Group created.'

def test_delete_group_route_not_exist(client):
    response = client.delete('/groups/test')
    assert response.status_code == 400
    assert b"Group test does not exist and so couldn't be deleted." in response.data

def test_delete_group_route_os_error(monkeypatch, client):
    monkeypatch.setattr('subprocess.run', lambda command, check, shell: CompletedProcess(['some_command'], returncode=0))
    monkeypatch.setattr('shutil.rmtree', lambda path: raise_(OSError))
    subprocess.call(["mkdir", "elephant_vending_machine/static/img/test"])
    response = client.delete('/groups/test')
    assert response.status_code == 400
    assert b'An error has occurred and the group could not be deleted' in response.data

def test_delete_group_happy_path(monkeypatch, client):
    monkeypatch.setattr('subprocess.run', lambda command, check, shell: CompletedProcess(['some_command'], returncode=0))
    subprocess.call(["mkdir", "elephant_vending_machine/static/img/test"])
    response = client.delete('/groups/test')
    assert response.status_code == 200
    assert b'Group test was successfully deleted.' in response.data 

def test_delete_fixations_group(monkeypatch, client):
    monkeypatch.setattr('subprocess.run', lambda command, check, shell: CompletedProcess(['some_command'], returncode=0))
    response = client.delete('/groups/Fixations')
    assert response.status_code == 400
    assert b'The fixations group cannot be deleted' in response.data 

def test_delete_group_no_connection(monkeypatch, client):
    monkeypatch.setattr('subprocess.run', lambda command, check, shell: raise_(CalledProcessError(1, ['ssh'])))
    subprocess.call(["mkdir", "elephant_vending_machine/static/img/test"])
    response = client.delete('/groups/test')
    assert response.status_code == 500
    assert json.loads(response.data)['message'] == ['Error: Failed to delete file from hosts. ', \
         'Group not deleted, please try again'] 

def test_get_group_route(client):
    subprocess.call(["mkdir", "elephant_vending_machine/static/img/test"])
    subprocess.call(["mkdir", "elephant_vending_machine/static/img/test2"])
    response = client.get('/groups')
    response_json_files = json.loads(response.data)['names']
    min_elements_expected = ["test","test2"]
    assert all(elem in response_json_files for elem in min_elements_expected)
    assert response.status_code == 200



