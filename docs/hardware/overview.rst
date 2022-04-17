Hardware Overview
=================

.. image:: ../_static/images/equipment_diagram.png
  :width: 800
  :alt: Connected hardware components

This is the high-level structure of the vending machine hardware. The
router is used to allow wireless access to the vending machine. The
Webserver Pi stores the stimuli, experiment, and log files and handles
all the logic of running experiments. 

The other three Raspberry Pis are used to interface with the additional
hardware. Each Sensor Pi is connected to a GPIO button, a monitor, and an LED strip. The GPIO buttons send
an input to the rasberry pis so it can be determined which stimuli was selected
and the appropriate outcome. The screens are used to display stimuli to the elephant. The LEDs are used
to provide instant visual feedback given the choice made on a button press.
LEDs display differing responses based on evaluation of the choice. Note: in the current design
the screen is the button that the elephant will push.


Parts List
##########

+-------------------------------+----------------------------------+----------+
| Component                     |  Model                           | Quantity |
+===============================+==================================+==========+
| Router                        | TP-Link Archer C1200             | 1        |
+-------------------------------+----------------------------------+----------+
| Sensor Pis                    | Two RPi 3B, One RPi 4 (4/15/22)  | 3        |
+-------------------------------+----------------------------------+----------+
| Server Pi                     | RPi 4                            | 1        |
+-------------------------------+----------------------------------+----------+
| GPIO Buttons                  | Unknown                          | 3        |
+-------------------------------+----------------------------------+----------+
| LED Strips                    | NeoPixel AdaFruit LED Strips     | 3        |
+-------------------------------+----------------------------------+----------+
| Arduino                       | Uno Rev3                         | 1        |
+-------------------------------+----------------------------------+----------+
| Monitor                       | Unknown                          | 3        |
+-------------------------------+----------------------------------+----------+
