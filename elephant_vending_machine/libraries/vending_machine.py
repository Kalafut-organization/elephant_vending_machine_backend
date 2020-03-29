"""Abstraction of physical "elephant vending machine"

This module  allows for display of images, control of LEDs,
and detecting motion sensor input on the machine.

.. todo::

   Integrate sensors dependent upon sensor interface info
"""

import multiprocessing as mp
import time
import sys
import spur
import maestro

SEMAPHORE = mp.Semaphore(1)
LEFT_SCREEN = 1
MIDDLE_SCREEN = 2
RIGHT_SCREEN = 3
SENSOR_THRESHOLD = 50
LEFT_SENSOR_PIN = 0
MIDDLE_SENSOR_PIN = 1
RIGHT_SENSOR_PIN = 2


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
    pin = None
    if grouping_number == LEFT_SCREEN:
        group = SensorGrouping(addresses[0], LEFT_SCREEN)
        pin = LEFT_SENSOR_PIN
    elif grouping_number == MIDDLE_SCREEN:
        group = SensorGrouping(addresses[1], MIDDLE_SCREEN)
        pin = MIDDLE_SENSOR_PIN
    else:
        group = SensorGrouping(addresses[2], RIGHT_SCREEN)
        pin = RIGHT_SENSOR_PIN
    result = group.wait_for_detection(pin, SENSOR_THRESHOLD)
    return result


class VendingMachine:
    """Provides an abstraction of the physical 'vending machine'.

    This class provides an abstraction of the overall machine, exposing SensorGrouping attributes
    for control of individual groupings of screen/sensor/LED strip.

    Parameters:
        addresses (list): A list of local IP addresses of the Raspberry Pis
        config (dict): A dictionary with configuration values, should contain
            REMOTE_LED_SCRIPT_DIRECTORY: a string representing the absolute path
            to the directory on the remote pis where the LED scripts are stored,
            REMOTE_IMAGE_DIRECTORY: a string representing the absolute path
            to where stimuli images are stored on the remote pis, SENSOR_THRESHOLD:
            the minimum sensor reading that will not count as motion detected.
            LEFT_SENSOR_PIN: an integer in the range 0-5 indicating which pin on
            the maestro board the left sensor pin is wired to. There will also be
            MIDDLE_SENSOR_PIN and RIGHT_SENSOR_PIN, with corresponding purposes.
            In the event these values are not passed in, defaults will be assigned
            as a fallback.
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
        if 'LEFT_SENSOR_PIN' not in self.config:
            self.config['LEFT_SENSOR_PIN'] = 0
        if 'MIDDLE_SENSOR_PIN' not in self.config:
            self.config['MIDDLE_SENSOR_PIN'] = 1
        if 'RIGHT_SENSOR_PIN' not in self.config:
            self.config['RIGHT_SENSOR_PIN'] = 2
        if 'SENSOR_THRESHOLD' not in self.config:
            self.config['SENSOR_THRESHOLD'] = 40
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
                group.group_id, self.addresses), callback=self.callback)
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

    def __init__(self, address, screen_identifier, config=None):
        self.group_id = screen_identifier
        self.correct_stimulus = False
        self.address = address
        self.config = config
        self.pid_of_previous_display_command = None

    def led_color_with_time(self, red, green, blue, display_time):
        """Displays the color specified by the given RGB values for *time* seconds.

        Parameters:
            red (int): A number in the range 0-255 specifying how much
                red should be in the RGB color display.
            green (int): A number in the range 0-255 specifying how much
                green should be in the RGB color display.
            blue (int): A number in the range 0-255 specifying how much
                blue should be in the RGB color display.
            display_time (int): The number of seconds that LEDs should display the color
                before returning to an "off" state.
        """
        shell = spur.SshShell(
            hostname=self.address,
            username='pi',
            missing_host_key=spur.ssh.MissingHostKey.accept,
            load_system_host_keys=False
        )
        with shell:
            shell.spawn(
                ['sudo', 'PYTHONPATH=\".:build/lib.linux-armv71-2.7\"',
                 'python',
                 # pylint: disable=line-too-long
                 # I don't see a good way to break this line up.
                 f'''{self.config['REMOTE_LED_SCRIPT_DIRECTORY']}/led.py {red} {green} {blue} {display_time}'''])

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

    def wait_for_detection(self, pin, threshold):
        """Waits until the motion sensor is activated and returns the group id

        Returns:
            group_id: The group id indicating which
                        SensorGrouping had it's motion detector triggered first.
        """
        input = maestro.Controller()
        reading = sys.maxsize
        while (reading > threshold) or (reading == 0):
            with SEMAPHORE:
                reading = int(input.getPosition(pin))
        return self.group_id
