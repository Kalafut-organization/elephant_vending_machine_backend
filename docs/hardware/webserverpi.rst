Configuring Webserver Pi
========================

Creating SSH Key
################
The webserver needs its own SSH key for authenticating with the Sensor Pis. This key
is required to be created before you set up the backend docker image.

#. Run :code:`ssh-keygen -t rsa`
#. Press enter to store the key in the default location
#. Press enter twice to create a key with no password

Copying the SSH Key
###################
The created SSH key must now be copied to the sensor Pis.

#. Ensure all four Pis are connected to the configured vending machine router via ethernet
#. Run :code:`ssh-copy-id pi@192.168.0.11`
#. Enter :code:`yes` and press enter
#. Enter the password :code:`raspberry`
#. Test that the key was copied successfully with `ssh pi@192.168.0.11`. It should not prompt you for a password
#. Enter :code:`exit` to end the SSH connection
#. Repeat the above steps for the other two sensor Pis with IPs :code:`192.168.0.12` and :code:`192.168.0.13`

Installing Docker and Docker-Compose
####################################
Docker is used to manage multiple services for the backend and ensure the backend runs across reboots.

#. Ensure the Pi is connected to the internet
#. Install the latest docker with :code:`curl -sSL https://get.docker.com | sh`
#. Add the pi user to the docker group with :code:`sudo usermod -aG docker pi`
#. Reboot the Pi
#. Install additional dependencies with :code:`sudo apt-get install -y libffi-dev libssl-dev`
#. Install Docker-Compose with :code:`sudo pip3 install docker-compose`

Installing and Starting the Backend
####################################
The following steps are required to start the frontend. Note you will likely want to
install front and back end at the same time, while connected to the internet, and then
connect the Pi to the project router and run the commands to start both the front and back ends.

#. Ensure the Pi is connected to the internet
#. Download the backend project with :code:`git clone https://github.com/Kalafut-organization/elephant_vending_machine_backend.git`
#. Use :code:`cd elephant_vending_machine_backend` to enter the project directory
#. Use :code:`cp ~/.ssh/id_rsa .` to copy the SSH key you generated previously into the project directory
#. Run :code:`docker-compose build --no-cached` to build the images
#. Connect the Pi to the configured project router via ethernet
#. Start the backend server with :code:`docker-compose up`

If you change the backend code and you aren't seeing these changes reflected in the running
Docker service, you may need to run :code:`docker system prune` and :code:`docker volume prune`.
Note that this will delete any of the experiments, stimuli, and logs stored on the server so be
cautious and back up any of these files you need to keep.

Installing and Starting the Frontend
####################################

#. Ensure the Pi is connected to the internet
#. Download the frontend project with :code:`git clone https://github.com/Kalafut-organization/elephant_vending_machine_frontend.git`
#. Update npm with :code:`curl https://www.npmjs.com/install.sh | sudo sh`
#. Navigate to the cloned directory
#. Ensure that the `.env` file has the address that the backend is using. For the backend running in docker, this should be `http://192.168.0.100`.
#. Run :code:`docker-compose build --no-cached` to build the images
   * For the image to build successfully, you will most likely need to temporarily remove the static IP of the pi.
#. Connect the Pi to the configured project router via ethernet
#. Start the backend server with :code:`docker-compose up`
