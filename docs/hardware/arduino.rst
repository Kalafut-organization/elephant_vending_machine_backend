Arduino Setup
=============

.. _arduino_config:

Initial Arduino Configuration
#############################

If for any reason code needs to be reuploaded to the Arduino, follow these instructions.

#. Install the Arduino IDE (https://www.arduino.cc/en/software) on your local machine
#. Launch the Arduino IDE
#. Connect your local machine to the Arduino using a USB A-Male to B-Male cable
#. Select Tools -> Board - > Arduino AVR Boards -> Arduino UNO
#. Select Tools -> Port -> And select the only available port
#. Upload the sketch
#. If successful, it should say "Done uploading"

Wiring the ESP8266
##################

**CAUTION:** The ESP8266 **MUST** be wired with 3.3V. Using 5V will damage the chip.

+-------------------------------+----------------------------------+
| ESP8266                       | Arduino                          |
+===============================+==================================+
| GND                           | GND                              |
+-------------------------------+----------------------------------+
| GPIO-2                        | Not connected (open)             |
+-------------------------------+----------------------------------+
| GPIO-0                        | Not connected (open)             |
+-------------------------------+----------------------------------+
| RXD                           | TX                               |
+-------------------------------+----------------------------------+
| TXD                           | RX                               |
+-------------------------------+----------------------------------+
| CHPD (EN)                     | 3.3V                             |
+-------------------------------+----------------------------------+
| RST                           | Not connected (open)             |
+-------------------------------+----------------------------------+
| VCC                           | 3.3V                             |
+-------------------------------+----------------------------------+

.. image:: https://hackster.imgix.net/uploads/attachments/719718/after_programming_8mrh0Aoco7.jpg?auto=compress%2Cformat&w=680&h=510&fit=max
  :width: 680
  :alt: ESP8266 Wiring

Putting the ESP8266 in programming mode
#######################################

In the unlikely event that the ESP8266 code needs to be updated or reuploaded, follow these instructions

#. Open the Arduino IDE
#. Go to File -> Preferences
#. Enter https://arduino.esp8266.com/stable/package_esp8266com_index.json into the Additional Board Manager URLs field.
#. Click OK
#. Go to Tools -> Board -> Boards Manager
#. Type "esp8266" in the field. Find the package with that name and click install.
#. Go to Tools -> Board -> ESP8266 Boards -> Generic ESP8266 Module
#. Select Tools -> Port -> And select the only available port
#. Wire the ESP8266 as follows

+-------------------------------+----------------------------------+
| ESP8266                       | Arduino                          |
+===============================+==================================+
| GND                           | GND                              |
+-------------------------------+----------------------------------+
| GPIO-2                        | Not connected (open)             |
+-------------------------------+----------------------------------+
| GPIO-0                        | GND                              |
+-------------------------------+----------------------------------+
| RXD                           | RX                               |
+-------------------------------+----------------------------------+
| TXD                           | TX                               |
+-------------------------------+----------------------------------+
| CHPD (EN)                     | 3.3V                             |
+-------------------------------+----------------------------------+
| RST                           | Not connected (open)             |
+-------------------------------+----------------------------------+
| VCC                           | 3.3V                             |
+-------------------------------+----------------------------------+

Next, follow these instructions in this order:

#. Connect the Arduino RESET pin to ground (not shown in schematic below, but required)
#. Connect the ESP8266 RST pin to ground for around half a second (The ESP8266's blue LED should flash)
#. Upload the sketch (If you get a "connection failed" error, try flashing the RST pin again)

.. image:: https://hackster.imgix.net/uploads/attachments/719715/during_programming_6GuB59TOuw.jpg?auto=compress%2Cformat&w=680&h=510&fit=max
  :width: 680
  :alt: ESP8266 Wiring


