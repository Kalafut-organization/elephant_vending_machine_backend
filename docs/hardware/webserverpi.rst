Configuring Webserver Pi
========================

Reference: https://www.pololu.com/docs/0J40/3.b

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
