Configuring Sensor Pis
=============================

First-Time Sensor Pi Configuration
###############################


Upon starting a Pi the first time you will be prompted to set some general system settings

#. Set the language and timezone
#. Leave the username/passwords as the default (pi and raspberry respectively)
#. Connect the pi to the internet

Install feh (used for displaying stimuli fullscreen)

#. Open a terminal
#. Enter the command :code:`sudo apt install feh`
#. Enter the password when (if) prompted

Setup the libraries used for lighting the LED strips

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
