Configuring Router
==================

First-Time Router Configuration
###############################
These are the necessary steps that must be taken to configure the router
in the event that it has been reset to factory defaults.

#. Connect your computer via ethernet to router port "Ethernet 1"
#. Navigate to :code:`192.168.0.1` in a web browser
#. Set the admin login password (originally "urfSj6GeUCntSmx9") and click "Next"
#. Set timezone to "Eastern Time" and click "Next"
#. Leave internet connetion type set to "Dynamic IP" and click "Next"
#. Leave "Do NOT Clone MAC Address" selected and click "Next"
#. Set both the 2.4GHz and 5GHz networks to use the SSID "Elephant-Vending-Machine" and set the password for both to the correct WiFi login password (originally "urfSj6GeUCntSmx9") then click "Next"
#. You should now be on the Summary page. Make sure all settings look correct and select "Save"

Configuring Static IPs for Raspberry Pis
########################################
The server code relies on the four Raspberry Pis having static IP addresses.
Note that the MAC Addresses are hardware specific, so if a Pi becomes faulty
and needs replaced, the following instructions will need to be adjusted. To
configure the static IPs, perform the following steps.

#. Connect to the "Elephant-Vending-Machine" WiFi
#. Access the router admin portal by navigating to :code:`192.168.0.1` in a web browser
#. Enter the router admin password
#. Click the "Advanced" tab
#. Select "Network" from the sidebar, then "DHCP Server" from the expanded menu
#. Add the following entries to the Address Reservation table:

+-------------------+---------------+--------------+--------------------+
|    MAC Address    |  IP Address   |  Description |  Enable This Entry |
+===================+===============+==============+====================+
| xx.xx.xx.xx       | 192.168.0.100 | Webserver Pi |         X          |
+-------------------+---------------+--------------+--------------------+
| B8-27-EB-2E-BF-23 | 192.168.0.11  | Sensor Pi 1  |         X          |
+-------------------+---------------+--------------+--------------------+
| B8-27-EB-6E-FF-5A | 192.168.0.12  | Sensor Pi 2  |         X          |
+-------------------+---------------+--------------+--------------------+
| E4-F5-01-07-1F-48 | 192.168.0.13  | Sensor Pi 3  |         X          |
+-------------------+---------------+--------------+--------------------+
| 84-CC-A8-83-EC-E8 | 192.168.0.14  | Arduino      |         X          |
+-------------------+---------------+--------------+--------------------+
