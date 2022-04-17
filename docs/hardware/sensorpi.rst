First-Time Configuration of Sensor Pis
======================================

Initial System Settings
#######################
Upon starting a Pi the first time you will be prompted to set some general system settings

#. Set the language and timezone
#. Leave the username/passwords as the default (pi and raspberry respectively)
#. Connect the pi to the internet (most easily done using a mobile hotspot, if available)

Configuring feh
###############
A program called feh must be installed. This is used for displaying stimuli images fullscreen.

#. Ensure the Pi is connected to the internet
#. Open a terminal
#. Enter the command :code:`sudo apt install feh`
#. Enter the password when (if) prompted

Configuring LED libraries
#########################
Setup the libraries used for controlling the LED strips.

#. Ensure the Pi is connected to the internet
#. Open a terminal and run :code:`sudo apt-get install gcc make build-essential python-dev git scons swig`
#. Run the command :code:`sudo nano /etc/modprobe.d/snd-blacklist.conf` and enter “blacklist snd_bcm2835”. Hit Ctrl-X Ctrl-Y Enter to save and exit
#. Run the command :code:`sudo nano /boot/config.txt` and change the line “dtparam=audio=on” to “#dtparam=audio=on” (comment it out)
#. Reboot the Pi
#. Open a terminal and enter :code:`git clone https://github.com/jgarff/rpi_ws281x`
#. Run the following
#. Run :code:`cd rpi_ws281x/`
#. Run :code:`sudo scons`
#. Run :code:`cd python`
#. Run :code:`sudo python setup.py build`
#. Run :code:`sudo python setup.py install`
#. Finally, you should copy the file "led.py" included in the backend directory into this directory (the python directory)

Enabling SSH
############
In order for the webserver to control the LEDs and displays remotely, SSH must be
enabled on all of the sensor Pis. You will get a warning about the default password
being set but this is fine since these Pis will be on an isolated network.

#. Click theRaspberry Pi icon in the top left corner of the screen
#. Click "Preferences" from the dropdown menu and then select "Raspberry Pi Configuration"
#. Select the "Interfaces" tab
#. Select "Enable" for SSH and then click "Save"
