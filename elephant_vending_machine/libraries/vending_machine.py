"""Abstract GPIO pin setup and interactions

This module contains funcitonality required to create
a vending machine instance, with nested SensorGrouping
instances used as an abstraction of the different screens
and associated sensors on the vending machines.

.. todo::

   Finish implementing
   Determine pin numbers
"""

<<<<<<< HEAD
import multiprocessing as mp
=======
import threading
>>>>>>> b20d1f05308eed0da56a961a480a8c8e507ef1cf
import time
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import MotionSensor, LED

<<<<<<< HEAD
=======
MOTION_PIN_VERTICAL = 1
MOTION_PIN_HORIZONTAL = 2
LED_PIN = 3

>>>>>>> b20d1f05308eed0da56a961a480a8c8e507ef1cf
class VendingMachine:
    """Provides an abstraction of the physical 'vending machine'.

    This class provides an abstraction of the sensors and screen associated
    with the elephant vending machine.
    """
<<<<<<< HEAD
    LEFT_SCREEN = 9
    MIDDLE_SCREEN = 10
    RIGHT_SCREEN = 11
    MOTION_PIN_VERTICAL = 1
    MOTION_PIN_HORIZONTAL = 2
    LED_PIN = 3

=======
>>>>>>> b20d1f05308eed0da56a961a480a8c8e507ef1cf
    def __init__(self, addresses):
        """Initialize an instance of VendingMachine.

        Provides an interface to the different sensors in divided by their associated screen.

        Parameters:
            addresses (list): A list of local IP addresses of the Raspberry Pis
        """

<<<<<<< HEAD
        self.left_group = self.SensorGrouping(addresses[0], LEFT_SCREEN)
        self.middle_group = self.SensorGrouping(addresses[1], MIDDLE_SCREEN)
        self.right_group = self.SensorGrouping(addresses[2], RIGHT_SCREEN)
=======
        self.group_one = self.SensorGrouping(addresses[0])
        self.group_two = self.SensorGrouping(addresses[1])
        self.group_three = self.SensorGrouping(addresses[2])
>>>>>>> b20d1f05308eed0da56a961a480a8c8e507ef1cf

    def wait_for_input():
        """Waits for input on the IR sensors.

        Returns:
<<<<<<< HEAD
            group: A constant corresponding to the group_id of the first sensor tripped
        """
        if __name__ == "__main__":
            pool = mp.Pool()
            result = [None] * 3
            for i in range(LEFT_SCREEN,RIGHT_SCREEN):
                pool.apply_async(func=worker, args=(i,), callback=callback)
            pool.close()
            pool.join()
            result = [ r in result if r is not None ]
            return result

    def worker(i):
        """ The function which is used by the pool. It calls the wait_for_detection() method
            for the passed associated SensorGrouping and returns the value returned by that method.
        """
        group = None
        if i == LEFT_SCREEN:
            group = self.left_group
        elif i == MIDDLE_SCREEN:
            group = self.middle_group
        else:
            group = self.right_group
        return group.wait_for_detection()

    def callback(t):
        if t in [ LEFT_SCREEN, MIDDLE_SCREEN, RIGHT_SCREEN ]:
            pool.terminate()
=======
            group: An integer (1, 2, or 3) corresponding to the first sensor tripped
        """
        return

>>>>>>> b20d1f05308eed0da56a961a480a8c8e507ef1cf
    class SensorGrouping:
        """Sensor interactions

        An abstraction of the sensors associated with a physical
        screen on the vending machine.
        """
<<<<<<< HEAD
        def __init__(self, address, screen_identifier):
            self.factory = PiGPIOFactory(host=address)
            self.group_id = screen_identifier
            self.ir_sensor_vertical = MotionSensor(MOTION_PIN_VERTICAL, pin_factory=self.factory)
            self.ir_sensor_horizontal = MotionSensor(MOTION_PIN_HORIZONTAL, pin_factory=self.factory)
            self.led = LED(LED_PIN, pin_factory=self.factory)
=======
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
>>>>>>> b20d1f05308eed0da56a961a480a8c8e507ef1cf

        def light_led():
            """Controls the lighting of LEDs for a given sensor grouping.
            """
<<<<<<< HEAD

        def wait_for_detection():
            """Waits until the motion sensor is activated and returns the group id
            """
            self.ir_sensor_vertical.wait_for_motion()
            return self.group_id
=======
            return

class IRSensorThread(threading.Thread):
    def __init__(self, thread_id):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
>>>>>>> b20d1f05308eed0da56a961a480a8c8e507ef1cf
