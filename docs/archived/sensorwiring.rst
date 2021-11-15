Sensor Wiring
=============

.. image:: ../_static/images/Sensor_Wiring_Diagram.png
  :width: 800
  :alt: Connected hardware components


#. Have the datasheets for the sensors and the Pololu servo controller open for reference (they are included with this documentation)
#. Wire pins 6 and 7 of each sensor to a 5V power supply (in our case we used the Pi’s, although with all sensors being used they will likely need dedicated power supplies) and to GND respectively.
#. Pin 3 on each sensor will be wired to one of the signal inputs on the Pololu. The software will expect the default to be the left sensor wired to channel 0, middle wired to channel 1, and right wired to channel 2. Pin 3 on the sensors is an analog output, and the Pololu board can read this value and be queried for the value over the USB connection.
