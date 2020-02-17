"""Abstract GPIO pin setup and interactions

This module contains funcitonality required to create
a vending machine instance, with nested SensorGrouping
instances used as an abstraction of the different screens
and associated sensors on the vending machines.

.. todo::

   Finish implementing
   Determine pin numbers
"""

import threading
import time
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import MotionSensor, LED

MOTION_PIN_VERTICAL = 1
MOTION_PIN_HORIZONTAL = 2
LED_PIN = 3

class VendingMachine:
    """Provides an abstraction of the physical 'vending machine'.

    This class provides an abstraction of the sensors and screen associated
    with the elephant vending machine.
    """
    def __init__(self, addresses):
        """Initialize an instance of VendingMachine.

        Provides an interface to the different sensors in divided by their associated screen.

        Parameters:
            addresses (list): A list of local IP addresses of the Raspberry Pis
        """

        self.group_one = self.SensorGrouping(addresses[0])
        self.group_two = self.SensorGrouping(addresses[1])
        self.group_three = self.SensorGrouping(addresses[2])

    def wait_for_input():
        """Waits for input on the IR sensors.

        Returns:
            group: An integer (1, 2, or 3) corresponding to the first sensor tripped
        """
        return

    class SensorGrouping:
        """Sensor interactions

        An abstraction of the sensors associated with a physical
        screen on the vending machine.
        """
        def __init__(self, address=''):
            self.factory = PiGPIOFactory(host=address)
            if address == '':
                self.ir_sensor = MotionSensor(MOTION_PIN_VERTICAL)
                self.ir_sensor = MotionSensor(MOTION_PIN_HORIZONTAL)
                self.led = LED(LED_PIN)
            else:
                self.ir_sensor = MotionSensor(MOTION_PIN_VERTICAL, pin_factory=self.factory)
                self.ir_sensor = MotionSensor(MOTION_PIN_HORIZONTAL, pin_factory=self.factory)
                self.led = LED(LED_PIN, pin_factory=self.factory)

        def light_led():
            """Controls the lighting of LEDs for a given sensor grouping.
            """
            return

class IRSensorThread(threading.Thread):
    def __init__(self, thread_id):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
