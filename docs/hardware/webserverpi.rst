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

Setting the IP
###################
The IP address of the webserver needs to be static. This should already be done, but these instructions still might be needed.
This is easiest to do with a monitor, keyboard, and mouse.

#. Right click on the internet icon in the top right of the raspberry pi toolbar.
#. Select "Wireless & Wired Network Settings"
#. Set "Configure" to "interface" and "eth0".
#. Ensure "Automatically configure empty options" is checked
#. Ensure "Disable IPv6" is checked
#. Set "IPv4 Address" to :code:`192.168.0.100`. (If you need to remove the static IP, ensure this field is blank.)
#. Click "Apply" and restart the pi.

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
If you just need to rebuild the image, skip to step 5.

#. Ensure the Pi is connected to the internet
#. Download the backend project with :code:`git clone https://github.com/Kalafut-organization/elephant_vending_machine_backend.git`
#. Use :code:`cd elephant_vending_machine_backend` to enter the project directory
#. Use :code:`cp ~/.ssh/id_rsa .` to copy the SSH key you generated previously into the project directory
#. Run :code:`docker-compose build --no-cached` to build the images (Ensure you have a good internet connection for this step. An ethernet connection is recommended.)
#. Connect the Pi to the configured project router via ethernet
#. Start the backend server with :code:`docker-compose up`

Installing and Starting the Frontend
####################################
If you just need to rebuild the image, skip to step 5.

#. Ensure the Pi is connected to the internet
#. Download the frontend project with :code:`git clone https://github.com/Kalafut-organization/elephant_vending_machine_frontend.git`
#. Update npm with :code:`curl https://www.npmjs.com/install.sh | sudo sh`
#. Navigate to the cloned directory
#. Ensure that the :code:`.env` file has the address that the backend is using. For the backend running in docker, this should be :code:`http://192.168.0.100`.
#. Remove the static IP of the pi. (see "Setting the static IP" above)
#. Run :code:`docker-compose build --no-cached` to build the images (Ensure you have a good internet connection for this step. An ethernet connection is recommended.)
#. Restore the static IP of the pi. (see "Setting the static IP" above)
#. Connect the Pi to the configured project router via ethernet
#. Start the backend server with :code:`docker-compose up`

Working in Development vs Production (Docker)
####################################

The purpose of getting this application to work with Docker is so that it can automatically run when the pi is turned on, 
and so that it can be easily run on different hardware in the future. During development, though, it is best to run 
the front and back end without docker so that realtime logging can be seen in terminals. Also, everytime a change is made,
docker images need to be rebuilt (which takes a while). See the readme files in each github repository to see how to run 
everything in development.   
If you are running in development, it is best to stop the docker containers first. To see if they are running, 
use the command :code:`docker ps`. You can stop them by navigating into each repository and running 
:code:`docker-compose down`. If you made changes and want to test running with docker, you just need to 
rebuild the images then start the containers (see "Installing and Starting the Frontend/Backend" above). 
The containers should then automatically start everytime the webserver pi is turned on.   
When you are switching between these two methods of running the code, you have to make sure the front end can still access
the back end. The address used for this is defined in :code:`.env` in the front end. When running in development, it should have port 5000.
When running in production with docker, it should not have a port.   
Finally, keep in mind that the front end is configured to run on port 3000 in development and port 4000 in production with docker.