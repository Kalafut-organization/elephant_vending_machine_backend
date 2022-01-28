Running System in Dev for testing
===================
Start-up frontend
#################
You will need to run commands on the server Pi though ssh network commands, this is included in these instructions

1. Connect to the same network as the Server Pi and navigate to your terminal
2. Run command, 'ssh pi@192.168.0.100'
3. A sign-in should appear, username is pi password is raspberry

you should now be in the Server Pi terminal

4. Enter the directory for the backend by running command 'cd elephant_vending_machine_frontend'
5. Ensure that the .env file has the address that the backend is using. For the backend running in development with Flask, this should be http://192.168.0.100:5000. -(Try Port 3000)
6. Run this command 'npm start'

the front end should open on your web browser

Start-up Backend
################
You will need to run commands on the server Pi though ssh network commands, this is included in these instructions

1. Connect to the same network as the Server Pi and navigate to your terminal
2. Run command, 'ssh pi@192.168.0.100'
3. A sign in should appear, username is pi password is raspberry
4. You should now be in the Server Pi terminal
5. Enter the directory for the backend by running command 'cd elephant_vending_machine_backend'
6. Run these commands to activate the backend

    'source .venv/bin/activate'
    
    'export FLASK_APP=elephant_vending_machine'
    
    'flask run --host=0.0.0.0'
    
the backend should be runnig now

6. To deactivate the back end run command 'deactivate' on the ssh terminal



