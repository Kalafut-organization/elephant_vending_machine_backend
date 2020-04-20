Configuring Webserver Pi
========================

Configuring Maestro Controller
##############################
The analogue-to-digital controller board used to interface with the sonar sensors requires some software setup.
Reference: https://www.pololu.com/docs/0J40/3.b

#. Ensure the Pi is connected to the internet
#. Download maestro-linux archive (the archive is included in the backend repository in case the reference site is unavailable)
#. Unzip it with the command: :code:`tar -xzvf archivename` where archivename is whatever it’s named
#. Follow the README inside the archive
#. You may have trouble with “libusb”. If you do, run :code:`sudo apt-get install libusb-1.0.0-dev`
#. Note that you will likely get an error about finding libmono-winforms. In this case, run :code:`sudo apt install mono-complete`
#. Run the command :code:`sudo cp 99-pololu.rules /etc/udev/rules.d/`
#. Run :code:`sudo udevadm control --reload-rules`
#. You should now plug in the maestro (if it was already plugged in, unplug it and run the udevadm command above again, then plug it in)
#. Issue the command :code:`./MaestroControlCenter` to open the configuration software for the Pololu board.
#. Navigate to the “Serial Settings” tab and set “Serial Mode” to “USB Dual Port”

Given that the sensors are wired to the Pololu board and power, you should now be able to view their readings on the “Status” page.

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
#. Install dependencies with :code:`npm install`
#. Connect the Pi to the configured project router via ethernet
#. Start the frontend with :code:`npm start`