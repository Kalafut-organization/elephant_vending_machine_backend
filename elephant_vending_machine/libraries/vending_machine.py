"""Abstraction of physical "elephant vending machine"

This module  allows for display of images, control of LEDs,
and detecting motion sensor input on the machine.

.. todo::

   Integrate sensors dependent upon sensor interface info
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


def worker(grouping_number, addresses):
    """ The function which is used by the pool. It calls the wait_for_detection() method
        for the passed associated SensorGrouping and returns the value returned by that method.

        Parameters:
            grouping_number (int): The integer representing which SensorGrouping the worker
                should monitor, value should be one of: LEFT_SCREEN, MIDDLE_SCREEN, RIGHT_SCREEN
            addresses (list): A list of local IP addresses of the Raspberry Pis

        Returns:
            int: One of LEFT_SCREEN, MIDDLE_SCREEN, or RIGHT_SCREEN, corresponding to
                the SensorGrouping which was selected
    """
    group = None
    if grouping_number == LEFT_SCREEN:
        group = SensorGrouping(addresses[0], LEFT_SCREEN)
    elif grouping_number == MIDDLE_SCREEN:
        group = SensorGrouping(addresses[1], MIDDLE_SCREEN)
    else:
        group = SensorGrouping(addresses[2], RIGHT_SCREEN)
    result = group.wait_for_detection()
    return result


class VendingMachine:
    """Provides an abstraction of the physical 'vending machine'.

    This class provides an abstraction of the overall machine, exposing SensorGrouping attributes
    for control of individual groupings of screen/sensor/LED strip.

    Parameters:
        addresses (list): A list of local IP addresses of the Raspberry Pis
        config (dict): A dictionary with configuration values, should contain
            REMOTE_LED_SCRIPT_DIRECTORY, a string representing the absolute path
            to the directory on the remote pis where the LED scripts are stored,
            and REMOTE_IMAGE_DIRECTORY, a string representing the absolute path
            to where stimuli images are stored on the remote pis. In the event these
            values are not passed in, defaults will be assigned as a fallback.
    """

    def __init__(self, addresses, config):
        self.addresses = addresses
        self.left_group = SensorGrouping(addresses[0], LEFT_SCREEN, config)
        self.middle_group = SensorGrouping(addresses[1], MIDDLE_SCREEN, config)
        self.right_group = SensorGrouping(addresses[2], RIGHT_SCREEN, config)
        if config is None:
            self.config = {}
        else:
            self.config = config
        if 'REMOTE_IMAGE_DIRECTORY' not in self.config:
            self.config['REMOTE_IMAGE_DIRECTORY'] = '/home/pi/elephant_vending_machine/images'
        if 'REMOTE_LED_SCRIPT_DIRECTORY' not in self.config:
            self.config['REMOTE_LED_SCRIPT_DIRECTORY'] = '/home/pi/rpi_ws281x/python'
        self.result = None
        self.pool = None

    def callback(self, selection):
        """When a worker process finishes, this method is invoked in the main thread
        and is passed the return value from the worker. As soon as this is called, the
        selection has been determined and the process pool is terminated.

        Parameters:
            selection (int): The return value of worker(), expected to be one
                of LEFT_SCREEN, MIDDLE_SCREEN, RIGHT_SCREEN.
        """
        quit_selection = selection
        self.result = quit_selection
        if quit_selection:
            self.pool.terminate()

    def wait_for_input(self, groups, timeout):
        """Waits for input on the motion sensors. If no motion is detected by the specified
        time to wait, returns with a result to indicate this.

        Parameters:
            groups (list[SensorGrouping]): The SensorGroupings which should be monitored for input.
            timeout (int): The amount of time in seconds to wait for input before timing out and
                returning 'timeout'.
        Returns:
            String: A string with value 'left', 'middle', 'right', or 'timeout', indicating
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

    Parameters:
        address (int): The local IP address of the Pi controlling the SensorGrouping
        config (dict): A dictionary with configuration values, should contain
            REMOTE_LED_SCRIPT_DIRECTORY, a string representing the absolute path
            to the directory on the remote pis where the LED scripts are stored,
            and REMOTE_IMAGE_DIRECTORY, a string representing the absolute path
            to where stimuli images are stored on the remote pis. In the event these
            values are not passed in, defaults will be assigned as a fallback.
    """

    # This class is only slightly over the recommended attribute limit and all are needed.
    # pylint: disable=too-many-instance-attributes
    def __init__(self, address, screen_identifier, config=None):
        self.factory = PiGPIOFactory(host=address)
        self.group_id = screen_identifier
        self.sensor = MotionSensor(MOTION_PIN, pin_factory=self.factory)
        self.led = LED(LED_PIN, pin_factory=self.factory)
        self.correct_stimulus = False
        self.address = address
        self.config = config
        self.pid_of_previous_display_command = None

    def LED_color_with_time(self, red, green, blue, time):
        """Displays the color specified by the given RGB values for *time* seconds.

        Parameters:
            red (int): A number in the range 0-255 specifying how much
                red should be in the RGB color display.
            green (int): A number in the range 0-255 specifying how much
                green should be in the RGB color display.
            blue (int): A number in the range 0-255 specifying how much
                blue should be in the RGB color display.
            time (int): The number of seconds that LEDs should display the color
                before returning to an "off" state.
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
