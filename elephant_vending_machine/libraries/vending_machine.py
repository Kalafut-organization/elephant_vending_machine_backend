

"""Abstraction of physical "elephant vending machine"

This module  allows for display of images, control of LEDs,
and detecting motion sensor input on the machine.
"""

import time
import subprocess
from pssh.clients import ParallelSSHClient
import requests 

LEFT_SCREEN = 1
MIDDLE_SCREEN = 2
RIGHT_SCREEN = 3

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
            to where stimuli images are stored on the remote pis
    """

    signal_sender = ''

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
        self.left_group = SensorGrouping(
            addresses[0], LEFT_SCREEN, self.config)
        self.middle_group = SensorGrouping(
            addresses[1], MIDDLE_SCREEN, self.config)
        self.right_group = SensorGrouping(
            addresses[2], RIGHT_SCREEN, self.config)
        self.result = None

    def wait_for_input(self, groups, timeout):
        """Waits for signal from the monitor pis. If no signal is received by the specified
        time to wait, returns with a result to indicate this.

        Parameters:
            groups (list[SensorGrouping]): The SensorGroupings which should be monitored for input.
            timeout (int): The amount of time in seconds to wait for input before timing out and
                returning 'timeout' (measured in milliseconds).
        Returns:
            String: A string with value 'left', 'middle', 'right', or 'timeout', indicating
            the selection or lack thereof.
        """
        selection = 'timeout'
        accepted_addresses = []
        for i in groups:
            accepted_addresses.append(i.address)

        start_time = get_current_time_milliseconds()
        elapsed_time = get_current_time_milliseconds() - start_time

        while self.signal_sender not in accepted_addresses and elapsed_time < timeout:
            elapsed_time = get_current_time_milliseconds() - start_time
        print(self.signal_sender)
        if self.signal_sender == self.addresses[0] and self.signal_sender in accepted_addresses:
            selection = 'left'
        elif self.signal_sender == self.addresses[1] and self.signal_sender in accepted_addresses:
            selection = 'middle'
        elif self.signal_sender == self.addresses[2] and self.signal_sender in accepted_addresses:
            selection = 'right'

        self.signal_sender = ''
        return selection

    def ssh_all_hosts(self, command):
        """ Sends given command to remote hosts via ssh

        Parameters:
            command: command to be sent over ssh """
        hosts = self.addresses
        client = ParallelSSHClient(hosts, user='pi')
        client.run_command(command)
        client.join()

    def display_images(self, images):
        """ Displays images on remote hosts via ssh

        Parameters:
            images: images to be displayed on the screens """
        new_images = []
        for image in images:
            if image in ('all_white_screen.png', 'fixation_stimuli.png', 'all_black_screen.png'):
                new_images.append(f'''/home/pi/elephant_vending_machine/default_img/{image}''')
            else:
                new_images.append(f'''{self.config['REMOTE_IMAGE_DIRECTORY']}/{image}''')
        hosts = self.addresses
        client = ParallelSSHClient(hosts, user='pi')
        self.ssh_all_hosts('xset -display :0 dpms force off')
        client.run_command('%s', host_args=(f'''DISPLAY=:0 feh -F -x -Y {new_images[0]} &''', \
         f'''DISPLAY=:0 feh -F -x -Y {new_images[1]} &''', \
         f'''DISPLAY=:0 feh -F -x -Y {new_images[2]} &'''))
        time.sleep(1)
        self.ssh_all_hosts('xset -display :0 dpms force on')

    @staticmethod
    def dispense_treat(index):
        """ Sends ssh command to dispense treat in corresponding tray

        Parameters:
            index: index (from 1 to 3) of the tray to be opened"""
        #headers = {'Content-Type':'text/plain'}
        response = requests.post(url="192.168.0.14/motor", data=str(index))
        print(response)

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

    def __init__(self, address, screen_identifier, config):
        self.group_id = screen_identifier
        self.address = address
        self.config = config
        self.pid_of_previous_display_command = None

    def led_color_with_time(self, red, green, blue, display_time):
        """Displays the color specified by the given RGB values for *time* milliseconds.

        Parameters:
            red (int): A number in the range 0-255 specifying how much
                red should be in the RGB color display.
            green (int): A number in the range 0-255 specifying how much
                green should be in the RGB color display.
            blue (int): A number in the range 0-255 specifying how much
                blue should be in the RGB color display.
            display_time (int): The number of milliseconds that LEDs should display the color
                before returning to an "off" state.
        """
        ssh_command = f'''ssh -oStrictHostKeyChecking=no -i /root/.ssh/id_rsa pi@{self.address} \
            sudo PYTHONPATH=\".:build/lib.linux-armv71-2.7\" python \
            {self.config['REMOTE_LED_SCRIPT_DIRECTORY']}/led.py \
            {red} {green} {blue} {display_time}'''
        subprocess.run(ssh_command, check=True, shell=True)

    # def display_on_screen(self, stimuli_name, default):
    #     """Displays the specified stimuli on the screen.
    #     Should only be called if the SensorGrouping config is not None

    #     Parameters:
    #         stimuli_name (str): The name of the file corresponding to the desired
    #                             stimuli to be displayed.
    #         default (bool): Whether the file is in the remote image
    #                             directory or the default image directory
    #     """
    #     path = ''
    #     if default:
    #         path = f'''/home/pi/elephant_vending_machine/default_img/{stimuli_name}'''
    #     else:
    #         path = f'''{self.config['REMOTE_IMAGE_DIRECTORY']}/{stimuli_name}'''

    #     subprocess.Popen(['ssh', f'''pi@{self.address}''', \
    #  'DISPLAY=:0', 'feh', '-F', '-x', '-Y', path, '&'])
