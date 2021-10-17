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
        subprocess.call(["rm", "elephant_vending_machine/static/img/GRP_TST/test_file.png"])
        subprocess.call(["rm", "elephant_vending_machine/static/img/GRP_TST/test_file2.jpg"])
        subprocess.call(["rm", "elephant_vending_machine/static/img/GRP_TST/blank.jpg"])
        subprocess.call(["rm", "-rf", "elephant_vending_machine/static/img/GRP_TST"])
        subprocess.call(["rm", "-rf", "elephant_vending_machine/static/img/GRP_TST2"])

def test_post_image_route_no_file(client):
    subprocess.call(["mkdir", "elephant_vending_machine/static/img/GRP_TST"])
    response = client.post('/GRP_TST/image')
    assert response.status_code == 400
    assert b'Error with request: No file field in body of request.' in response.data

def test_post_image_route_empty_filename(client):
    subprocess.call(["mkdir", "elephant_vending_machine/static/img/GRP_TST"])
    data = {'file': (BytesIO(b"Testing: \x00\x01"), '')}
    response = client.post('/GRP_TST/image', data=data) 
    assert response.status_code == 400
    assert b'Error with request: File field in body of response with no file present.' in response.data

def test_post_image_route_with_file_bad_extension(client):
    subprocess.call(["mkdir", "elephant_vending_machine/static/img/GRP_TST"])
    data = {'file': (BytesIO(b"Testing: \x00\x01"), 'test_file.sh')}
    response = client.post('/GRP_TST/image', data=data) 
    assert response.status_code == 400
    assert b'Error with request: File extension not allowed.' in response.data

def test_post_image_route_with_file(monkeypatch, client):
    subprocess.call(["mkdir", "elephant_vending_machine/static/img/GRP_TST"])
    monkeypatch.setattr('werkzeug.datastructures.FileStorage.save', lambda save_path, filename: "" )
    monkeypatch.setattr('subprocess.run', lambda command, check, shell: CompletedProcess(['some_command'], returncode=0))
    data = {'file': (BytesIO(b"Testing: \x00\x01"), 'test_file.png')}
    response = client.post('/GRP_TST/image', data=data) 
    assert response.status_code == 201
    assert b'Success: Image saved.' in response.data

def test_post_image_route_copying_exception(monkeypatch, client):
    subprocess.call(["mkdir", "elephant_vending_machine/static/img/GRP_TST"])
    monkeypatch.setattr('subprocess.run', lambda command, check, shell: raise_(CalledProcessError(1, ['ssh'])))
    subprocess.call(["touch", "elephant_vending_machine/static/img/GRP_TST/test_delete.jpg"])
    data = {'file': (BytesIO(b"Testing: \x00\x01"), 'test_delete.png')}
    response = client.post('/GRP_TST/image', data=data) 
    assert response.status_code == 500
    assert b"Error: Failed to copy file to hosts. ", \
        "Image not saved, please try again" in response.data

def test_get_image_endpoint(client):
    subprocess.call(["mkdir", "elephant_vending_machine/static/img/GRP_TST"])
    subprocess.call(["touch", "elephant_vending_machine/static/img/GRP_TST/test_file.png"])
    subprocess.call(["touch", "elephant_vending_machine/static/img/GRP_TST/test_file2.jpg"])
    response = client.get('/GRP_TST')
    response_json_files = json.loads(response.data)['files']
    min_elements_expected = ["http://localhost/static/img/GRP_TST/test_file.png","http://localhost/static/img/GRP_TST/test_file2.jpg"]
    assert all(elem in response_json_files for elem in min_elements_expected)
    assert response.status_code == 200

def test_delete_image_happy_path(monkeypatch, client):
    subprocess.call(["mkdir", "elephant_vending_machine/static/img/GRP_TST"])
    subprocess.call(["touch", "elephant_vending_machine/static/img/GRP_TST/blank.jpg"])
    monkeypatch.setattr('subprocess.run', lambda command, check, shell: CompletedProcess(['some_command'], returncode=0))
    response = client.delete('/image/GRP_TST/blank.jpg')
    assert response.status_code == 200
    assert json.loads(response.data)['message'] == 'File blank.jpg was successfully deleted.'
    
def test_delete_image_route_copying_exception(monkeypatch, client):
    subprocess.call(["mkdir", "elephant_vending_machine/static/img/GRP_TST"])
    monkeypatch.setattr('subprocess.run', lambda command, check, shell: raise_(CalledProcessError(1, ['ssh'])))
    subprocess.call(["touch", "elephant_vending_machine/static/img/GRP_TST/test_delete.jpg"])
    response = client.delete('/image/GRP_TST/test_delete.jpg')
    assert b"Error: Failed to delete file from hosts. ", \
        "Image not deleted, please try again" in response.data
    assert response.status_code == 500
    
def test_delete_image_no_group(monkeypatch, client):
    monkeypatch.setattr('subprocess.run', lambda command, check, shell: CompletedProcess(['some_command'], returncode=0))
    response = client.delete('/image/GRP_TST/blank.jpg')
    assert response.status_code == 400
    assert json.loads(response.data)['message'] == 'Group GRP_TST does not exist'

def test_delete_image_file_not_found(client):
    subprocess.call(["mkdir", "elephant_vending_machine/static/img/GRP_TST"])
    response = client.delete('/image/GRP_TST/blank.jpg')
    assert response.status_code == 400
    assert json.loads(response.data)['message'] == 'File blank.jpg does not exist and so couldn\'t be deleted.'

def test_delete_image_is_a_directory_exception(client, monkeypatch):
    subprocess.call(["mkdir", "elephant_vending_machine/static/img/GRP_TST"])
    subprocess.call(["touch", "elephant_vending_machine/static/img/GRP_TST/blank.jpg"])
    monkeypatch.setattr('subprocess.run', lambda command, check, shell: CompletedProcess(['some_command'], returncode=0))
    monkeypatch.setattr('os.remove', lambda file: (_ for _ in ()).throw(IsADirectoryError))
    response = client.delete('/image/GRP_TST/blank.jpg')
    assert response.status_code == 400
    assert json.loads(response.data)['message'] == 'blank.jpg exists, but is a directory and not a file. Deletion failed.'

def test_image_copy_to_group_happy_path(client, monkeypatch):
    subprocess.call(["mkdir", "elephant_vending_machine/static/img/GRP_TST"])
    subprocess.call(["mkdir", "elephant_vending_machine/static/img/GRP_TST2"])
    subprocess.call(["touch", "elephant_vending_machine/static/img/GRP_TST/blank.jpg"])
    monkeypatch.setattr('subprocess.run', lambda command, check, shell: CompletedProcess(['some_command'], returncode=0))
    data = {"name": "GRP_TST2"}
    response = client.post("/GRP_TST/blank.jpg/copy", data=data)
    assert response.status_code == 200
    assert json.loads(response.data)['message'] == "File blank.jpg was successfully copied to group 'GRP_TST2'."

def test_image_copy_to_group_no_group2(client):
    data = {"name": "GRP_TST2"}
    response = client.post("/GRP_TST1/blank.jpg/copy", data=data)
    assert response.status_code == 400
    assert json.loads(response.data)['message'] == 'Error with request: GRP_TST2 is not an existing directory'
    
def test_image_copy_to_group_no_image(client):
    subprocess.call(["mkdir", "elephant_vending_machine/static/img/GRP_TST"])
    data = {"name": "GRP_TST"}
    response = client.post("/GRP_TST1/blank.jpg/copy", data=data)
    assert response.status_code == 400
    assert json.loads(response.data)['message'] == 'Error with request: blank.jpg does not exist'

def test_image_copy_to_group_copying_exception(client, monkeypatch):
    subprocess.call(["mkdir", "elephant_vending_machine/static/img/GRP_TST"])
    subprocess.call(["mkdir", "elephant_vending_machine/static/img/GRP_TST2"])
    subprocess.call(["touch", "elephant_vending_machine/static/img/GRP_TST/blank.jpg"])
    monkeypatch.setattr('subprocess.run', lambda command, check, shell: raise_(CalledProcessError(1, ['ssh'])))
    data = {"name": "GRP_TST2"}
    response = client.post("/GRP_TST/blank.jpg/copy", data=data)
    assert response.status_code == 500
    assert json.loads(response.data)['message'] == ['Error: Failed to copy file to hosts. ', 'Image not copied, please try again'] 