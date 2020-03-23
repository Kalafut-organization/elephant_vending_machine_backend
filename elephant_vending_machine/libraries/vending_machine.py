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
import time
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import MotionSensor, LED
import spur


LEFT_SCREEN = 1
MIDDLE_SCREEN = 2
RIGHT_SCREEN = 3
MOTION_PIN = 10
LED_PIN = 3
RED = 33
GREEN = 34


def worker(i, addresses):
    """ The function which is used by the pool. It calls the wait_for_detection() method
        for the passed associated SensorGrouping and returns the value returned by that method.
    """
    group = None
    if i == LEFT_SCREEN:
        group = SensorGrouping(addresses[0], LEFT_SCREEN)
    elif i == MIDDLE_SCREEN:
        group = SensorGrouping(addresses[1], MIDDLE_SCREEN)
    else:
        group = SensorGrouping(addresses[2], RIGHT_SCREEN)
    result = group.wait_for_detection()
    return result


class VendingMachine:
    """Provides an abstraction of the physical 'vending machine'.

    This class provides an abstraction of the sensors and screen associated
    with the elephant vending machine.
    """

    def __init__(self, addresses, config):
        """Initialize an instance of VendingMachine.

        Provides an interface to the different sensors in divided by their associated screen.

        Parameters:
            addresses (list): A list of local IP addresses of the Raspberry Pis
            config (dict): The configuration values of the Flask server
        """

        self.addresses = addresses
        self.left_group = SensorGrouping(addresses[0], LEFT_SCREEN, config)
        self.middle_group = SensorGrouping(addresses[1], MIDDLE_SCREEN, config)
        self.right_group = SensorGrouping(addresses[2], RIGHT_SCREEN, config)
        self.config = config
        self.result = None
        self.pool = None

    def callback(self, selection):
        """When a worker process finishes, this method is invoked in the main thread
        and is passed the return value from the worker. As soon as this is called, the
        selection has been determined and the process pool is terminated.

        """
        quit_selection = selection
        self.result = quit_selection
        if quit_selection:
            self.pool.terminate()

    def wait_for_input(self, groups, timeout):
        """Waits for input on the motion sensors. If no motion is detected by the specified
        time to wait, returns with a result to indicate this.

        Returns:
            selection: A string with value 'left', 'middle', 'right', or 'timeout', indicating
            the selection or lack thereof.
        """
        self.result = None
        start_time = time.perf_counter()
        selection = 'timeout'
        self.pool = mp.Pool()
        for group in groups:
            self.pool.apply_async(func=worker, args=(
                group.get_group_id, self.addresses), callback=self.callback)
        while self.result is None:
            current_time = time.perf_counter()
            if current_time - start_time > timeout:
                self.pool.terminate()
                break
        self.pool.close()
        self.pool.join()
        if self.result == LEFT_SCREEN:
            selection = 'left'
        elif self.result == MIDDLE_SCREEN:
            selection = 'middle'
        elif self.result == RIGHT_SCREEN:
            selection = 'right'
        return selection


class SensorGrouping:
    """Provides an abstraction of the devices controlled by Raspberry Pis.

    Pi's will have an LED strip, a distance measurement device, and a screen.
    This class will provide utilities for interacting with individual sensors.
    """

    # This class is only one attribute over the recommended limit and all are needed.
    # pylint: disable=too-many-instance-attributes
    def __init__(self, address, screen_identifier, config=None):
        """Initialize an instance of VendingMachine.

        Provides an interface to the different sensors in divided by their associated screen.

         Parameters:
            address (str): The local network address of the Raspberry Pi controlling the sensors
            screen_identifier (int): A integer
            config (dict): The configuration values of the Flask server
        """
        self.factory = PiGPIOFactory(host=address)
        self.group_id = screen_identifier
        self.sensor = MotionSensor(MOTION_PIN, pin_factory=self.factory)
        self.led = LED(LED_PIN, pin_factory=self.factory)
        self.correct_stimulus = False
        self.address = address
        self.config = config
        self.pid_of_previous_display_command = None

    def change_led(self, color):
        """Controls the lighting of LEDs for a given sensor grouping.

        Parameters:
            state (int): The desired state of the LED.
        """
        shell = spur.SshShell(
            hostname=self.address,
            username='pi',
            missing_host_key=spur.ssh.MissingHostKey.accept,
            load_system_host_keys=False
        )
        with shell:
            shell.run(
                ['sudo', 'PYTHONPATH=\".:build/lib.linux-armv71-2.7\"',
                 'python', f'''{self.config['REMOTE_LED_SCRIPT_DIRECTORY']}/{color}.py'''])

    def get_group_id(self):
        """Getter for SensorGrouping id

        """
        return self.group_id

    def display_on_screen(self, stimuli_name, correct_answer):
        """Displays the specified stimuli on the screen.
        Should only be called if the SensorGrouping config is not None

        Parameters:
            stimuli_name (str): The name of the file corresponding to the desired
                                stimuli to be displayed.
            correct_answer (boolean): Denotes whether this is the desired selection.
        """
        self.correct_stimulus = correct_answer
        shell = spur.SshShell(
            hostname=self.address,
            username='pi',
            missing_host_key=spur.ssh.MissingHostKey.accept,
            load_system_host_keys=False
        )
        with shell:
            result = shell.spawn(['feh', '-F',
                                  f'''{self.config['REMOTE_IMAGE_DIRECTORY']}/{stimuli_name}''',
                                  '&'], update_env={'DISPLAY': ':0'}, store_pid=True).pid
        self.pid_of_previous_display_command = int(result)

    def wait_for_detection(self):
        """Waits until the motion sensor is activated and returns the group id

        Returns:
            group_id: The group id indicating which
                        SensorGrouping had it's motion detector triggered first.
        """
        return self.group_id
