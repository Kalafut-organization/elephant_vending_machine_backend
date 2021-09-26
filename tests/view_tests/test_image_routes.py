import pytest
import subprocess
from io import BytesIO
import json

from elephant_vending_machine import elephant_vending_machine
from subprocess import CompletedProcess, CalledProcessError

def raise_(ex):
    raise ex

@pytest.fixture
def client():
    elephant_vending_machine.APP.config['TESTING'] = True

    with elephant_vending_machine.APP.test_client() as client:
        yield client
        subprocess.call(["rm", "elephant_vending_machine/static/img/test_file.png"])
        subprocess.call(["rm", "elephant_vending_machine/static/img/test_file2.jpg"])
        subprocess.call(["rm", "elephant_vending_machine/static/img/blank.jpg"])

def test_post_image_route_no_file(client):
    response = client.post('/image')
    assert response.status_code == 400
    assert b'Error with request: No file field in body of request.' in response.data

def test_post_image_route_empty_filename(client):
    data = {'file': (BytesIO(b"Testing: \x00\x01"), '')}
    response = client.post('/image', data=data) 
    assert response.status_code == 400
    assert b'Error with request: File field in body of response with no file present.' in response.data

def test_post_image_route_with_file_bad_extension(client):
    data = {'file': (BytesIO(b"Testing: \x00\x01"), 'test_file.sh')}
    response = client.post('/image', data=data) 
    assert response.status_code == 400
    assert b'Error with request: File extension not allowed.' in response.data

def test_post_image_route_with_file(monkeypatch, client):
    monkeypatch.setattr('werkzeug.datastructures.FileStorage.save', lambda save_path, filename: "" )
    monkeypatch.setattr('subprocess.run', lambda command, check, shell: CompletedProcess(['some_command'], returncode=0))
    data = {'file': (BytesIO(b"Testing: \x00\x01"), 'test_file.png')}
    response = client.post('/image', data=data) 
    assert response.status_code == 201
    assert b'Success: Image saved.' in response.data

def test_post_image_route_copying_exception(monkeypatch, client):
    monkeypatch.setattr('werkzeug.datastructures.FileStorage.save', lambda save_path, filename: "" )
    monkeypatch.setattr('subprocess.run', lambda command, check, shell: raise_(CalledProcessError(1, ['ssh'])))
    subprocess.call(["touch", "elephant_vending_machine/static/img/test_file.jpg"])
    data = {'file': (BytesIO(b"Testing: \x00\x01"), 'test_file.png')}
    response = client.post('/image', data=data) 
    assert response.status_code == 500
    assert b"Error: Failed to copy file to hosts. ", \
        "Image not saved, please try again" in response.data

def test_get_image_endpoint(client):
    subprocess.call(["touch", "elephant_vending_machine/static/img/test_file.png"])
    subprocess.call(["touch", "elephant_vending_machine/static/img/test_file2.jpg"])
    response = client.get('/image')
    response_json_files = json.loads(response.data)['files']
    min_elements_expected = ["http://localhost/static/img/test_file.png","http://localhost/static/img/test_file2.jpg"]
    assert all(elem in response_json_files for elem in min_elements_expected)
    assert response.status_code == 200

def test_delete_image_happy_path(monkeypatch, client):
    subprocess.call(["touch", "elephant_vending_machine/static/img/blank.jpg"])
    monkeypatch.setattr('subprocess.run', lambda command, check, shell: CompletedProcess(['some_command'], returncode=0))
    response = client.delete('/image/blank.jpg')
    assert response.status_code == 200
    assert json.loads(response.data)['message'] == 'File blank.jpg was successfully deleted.'

def test_delete_image_file_not_found(client):
    response = client.delete('/image/blank.jpg')
    assert response.status_code == 400
    assert json.loads(response.data)['message'] == 'File blank.jpg does not exist and so couldn\'t be deleted.'

def test_delete_image_is_a_directory_exception(client, monkeypatch):
    subprocess.call(["touch", "elephant_vending_machine/static/img/blank.jpg"])
    monkeypatch.setattr('os.remove', lambda file: (_ for _ in ()).throw(IsADirectoryError))
    response = client.delete('/image/blank.jpg')
    assert response.status_code == 400
    assert json.loads(response.data)['message'] == 'blank.jpg exists, but is a directory and not a file. Deletion failed.'