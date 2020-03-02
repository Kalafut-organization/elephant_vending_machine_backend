"""Abstract GPIO pin setup and interactions

This module contains funcitonality required to create
a vending machine instance, with nested SensorGrouping
instances used as an abstraction of the different screens
and associated sensors on the vending machines.

.. todo::

   Finish implementing
   Determine pin numbers
"""

import multiprocessing as mp
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import MotionSensor, LED


LEFT_SCREEN = 9
MIDDLE_SCREEN = 10
RIGHT_SCREEN = 11
MOTION_PIN_VERTICAL = 1
MOTION_PIN_HORIZONTAL = 2
LED_PIN = 3
RED = 33
GREEN = 34

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

        self.left_group = SensorGrouping(addresses[0], LEFT_SCREEN)
        self.middle_group = SensorGrouping(addresses[1], MIDDLE_SCREEN)
        self.right_group = SensorGrouping(addresses[2], RIGHT_SCREEN)

    def wait_for_input(self):
        """Waits for input on the IR sensors.

        Returns:
            group: A constant (int) corresponding to the group_id of the first sensor tripped
        """
        if __name__ == "__main__":
            pool = mp.Pool()
            result = [None] * 3
            for i in range(LEFT_SCREEN, RIGHT_SCREEN):
                pool.apply_async(func=worker, args=(i,), callback=callback)
            pool.close()
            pool.join()
            final_value = [r for r in result if r is not None]
            return final_value

    def worker(self, i):
        """ The function which is used by the pool. It calls the wait_for_detection() method
            for the passed associated SensorGrouping and returns the value returned by that method.
        """
        print("Called for " + i)
        group = None
        if i == LEFT_SCREEN:
            group = self.left_group
        elif i == MIDDLE_SCREEN:
            group = self.middle_group
        else:
            group = self.right_group
        return group.wait_for_detection()

    def callback(self, t):
        if t in [LEFT_SCREEN, MIDDLE_SCREEN, RIGHT_SCREEN]:
            pool.terminate()

class SensorGrouping:
    """Sensor interactions

    An abstraction of the sensors associated with a physical
    screen on the vending machine.
    """
    def __init__(self, address, screen_identifier):
        self.factory = PiGPIOFactory(host=address)
        self.group_id = screen_identifier
        self.ir_sensor_vertical = MotionSensor(MOTION_PIN_VERTICAL, pin_factory=self.factory)
        self.ir_sensor_horizontal = MotionSensor(MOTION_PIN_HORIZONTAL, pin_factory=self.factory)
        self.led = LED(LED_PIN, pin_factory=self.factory)
        self.correct_stimulus = false

    def change_led(self, state):
        """Controls the lighting of LEDs for a given sensor grouping.

        Parameters:
            state (int): The desired state of the LED.
        """

    def display_on_screen(self, stimuli_name, correct_answer):
        """Displays the specified stimuli on the screen.

        Parameters:
            stimuli_name (str): The name of the file corresponding to the desired
                                stimuli to be displayed.
            correct_answer (boolean): Denotes whether this is the desired selection.
        """
        self.correct_stimulus = correct_answer

    def wait_for_detection_vertical(self):
        """Waits until the motion sensor is activated and returns the group id

        Returns:
            group_id: The group id indicating which SensorGrouping had it's IR sensor(s) triggered first.
        """
        self.ir_sensor_vertical.wait_for_motion()
        return self.group_id

     def wait_for_detection_horizontal(self):
        """Waits until the motion sensor is activated and returns the group id

        Returns:
            group_id: The group id indicating which SensorGrouping had it's IR sensor(s) triggered first.
        """
        self.ir_sensor_horizontal.wait_for_motion()
        return self.group_id
