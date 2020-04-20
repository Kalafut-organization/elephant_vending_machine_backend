"""Abstraction of physical "elephant vending machine"

This module  allows for display of images, control of LEDs,
and detecting motion sensor input on the machine.
"""

import time
import subprocess
import spur
import maestro

LEFT_SCREEN = 1
MIDDLE_SCREEN = 2
RIGHT_SCREEN = 3
SENSOR_THRESHOLD = 20
LEFT_SENSOR_PIN = 0
MIDDLE_SENSOR_PIN = 1
RIGHT_SENSOR_PIN = 2

def get_current_time_milliseconds():
    """Timeouts will be handled in milliseconds.
    This method will return the time elapsed since
    the CPU recieved power in nanoseconds, and thus
    is only useful for measuring relative time intervals,
    it is not adjusted for the absolute time.
    """
    return time.perf_counter() * 1000

# This is how our Vending Machine would be logically organized, ignoring linting warning.
# pylint: disable=too-few-public-methods
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

    def __init__(self, addresses, config=None):
        self.addresses = addresses
        if config is None:
            self.config = {}
        else:
            self.config = config
        if 'REMOTE_IMAGE_DIRECTORY' not in self.config:
            self.config['REMOTE_IMAGE_DIRECTORY'] = '/home/pi/elephant_vending_machine/images'
        if 'REMOTE_LED_SCRIPT_DIRECTORY' not in self.config:
            self.config['REMOTE_LED_SCRIPT_DIRECTORY'] = '/home/pi/rpi_ws281x/python'
        if 'LEFT_SENSOR_PIN' not in self.config:
            self.config['LEFT_SENSOR_PIN'] = LEFT_SENSOR_PIN
        if 'MIDDLE_SENSOR_PIN' not in self.config:
            self.config['MIDDLE_SENSOR_PIN'] = MIDDLE_SENSOR_PIN
        if 'RIGHT_SENSOR_PIN' not in self.config:
            self.config['RIGHT_SENSOR_PIN'] = RIGHT_SENSOR_PIN
        if 'SENSOR_THRESHOLD' not in self.config:
            self.config['SENSOR_THRESHOLD'] = SENSOR_THRESHOLD
        self.left_group = SensorGrouping(
            addresses[0], LEFT_SCREEN, self.config['LEFT_SENSOR_PIN'], self.config)
        self.middle_group = SensorGrouping(
            addresses[1], MIDDLE_SCREEN, self.config['MIDDLE_SENSOR_PIN'], self.config)
        self.right_group = SensorGrouping(
            addresses[2], RIGHT_SCREEN, self.config['RIGHT_SENSOR_PIN'], self.config)
        self.result = None

    @staticmethod
    def wait_for_input(groups, timeout):
        """Waits for input on the motion sensors. If no motion is detected by the specified
        time to wait, returns with a result to indicate this.

        Parameters:
            groups (list[SensorGrouping]): The SensorGroupings which should be monitored for input.
            timeout (int): The amount of time in seconds to wait for input before timing out and
                returning 'timeout' (measured in milliseconds).
        Returns:
            String: A string with value 'left', 'middle', 'right', or 'timeout', indicating
            the selection or lack thereof.
        """
        reader = maestro.Controller()
        selection = 'timeout'
        start_time = get_current_time_milliseconds()
        elapsed_time = get_current_time_milliseconds() - start_time
        readings = [1000] * len(groups)
        while (all(reading >= SENSOR_THRESHOLD or reading == 0 for reading in readings) and
               elapsed_time < timeout):
            # range(len()) has less overhead than enumerate
            # pylint: disable=consider-using-enumerate
            for i in range(len(groups)):
                readings[i] = reader.getPosition(groups[i].sensor_pin)
            elapsed_time = get_current_time_milliseconds() - start_time
        selection_index = None
        # range(len()) has less overhead than enumerate
        # pylint: disable=consider-using-enumerate
        for i in range(len(readings)):
            if SENSOR_THRESHOLD > readings[i] > 0:
                selection_index = i
                break
        if selection_index is not None:
            if groups[selection_index].group_id == LEFT_SCREEN:
                selection = 'left'
            elif groups[selection_index].group_id == MIDDLE_SCREEN:
                selection = 'middle'
            else:
                selection = 'right'
        return selection


class SensorGrouping:
    """Provides an abstraction of the devices controlled by Raspberry Pis.

    Pi's will have an LED strip and a screen.
    This class will provide utilities for interacting with individual LED strips and screens.

    Parameters:
        address (int): The local IP address of the Pi controlling the SensorGrouping
        config (dict): A dictionary with configuration values, should contain
            REMOTE_LED_SCRIPT_DIRECTORY, a string representing the absolute path
            to the directory on the remote pis where the LED scripts are stored,
            and REMOTE_IMAGE_DIRECTORY, a string representing the absolute path
            to where stimuli images are stored on the remote pis. In the event these
            values are not passed in, defaults will be assigned as a fallback.
    """

    def __init__(self, address, screen_identifier, sensor_pin, config):
        self.group_id = screen_identifier
        self.correct_stimulus = False
        self.address = address
        self.sensor_pin = sensor_pin
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
        ssh_command = f'''ssh -oStrictHostKeyChecking=no -i /root/.ssh/id_rsa pi@{self.address} \
            sudo PYTHONPATH=\".:build/lib.linux-armv71-2.7\" python \
            {self.config['REMOTE_LED_SCRIPT_DIRECTORY']}/led.py \
            {red} {green} {blue} {display_time}'''
        subprocess.run(ssh_command, check=True, shell=True)

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
