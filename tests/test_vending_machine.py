from elephant_vending_machine.libraries.vending_machine import VendingMachine, SensorGrouping, LEFT_SCREEN
from subprocess import CompletedProcess, CalledProcessError
import pytest
import time


def new_init(self):
    self.getPosition = lambda pin_number: 5 if pin_number == 0 else 0


def new_init_timeout(self):
    self.getPosition = lambda pin_number: 0

def raise_(ex):
    raise ex

def test_wait_for_input(monkeypatch):
    monkeypatch.setattr('maestro.Controller.__init__', new_init)
    vending_machine = VendingMachine(['1', '2', '3'])
    result = vending_machine.wait_for_input(
        [vending_machine.left_group, vending_machine.right_group], 5000)
    assert result == 'left'


def test_wait_for_input_timeout(monkeypatch):
    monkeypatch.setattr(
        'maestro.Controller.__init__', new_init_timeout)
    vending_machine = VendingMachine(['1', '2', '3'])
    result = vending_machine.wait_for_input(
        [vending_machine.left_group, vending_machine.right_group], 1000)
    assert result == 'timeout'


@pytest.mark.skip(reason="There is no good way to unit test an ssh connection and visual display with pytest.")
def test_display(monkeypatch):
    vending_machine = VendingMachine(['192.168.1.35', '2', '3'], {
                                     'REMOTE_IMAGE_DIRECTORY': '/home/pi/elephant_vending_machine/images'})
    vending_machine.left_group.display_on_screen('elephant.jpg', True)
    time.sleep(3)
    vending_machine.left_group.display_on_screen('elephant2.jpg', True)
    assert type(
        vending_machine.left_group.pid_of_previous_display_command) is int

def test_led_happy_path(monkeypatch):
    vending_machine = VendingMachine(['192.168.1.35', '2', '3'], {})
    monkeypatch.setattr('subprocess.run', lambda command, check, shell: CompletedProcess(['some_command'], returncode=0))
    try:
        vending_machine.left_group.led_color_with_time(255, 255, 255, 1000)
    except CalledProcessError:
        pytest.fail("Unexpected LED SSH command failure")

def test_led_exception_if_ssh_fails(monkeypatch):
    with pytest.raises(CalledProcessError):
        vending_machine = VendingMachine(['192.168.1.35', '2', '3'], {})
        monkeypatch.setattr('subprocess.run', lambda command, check, shell: raise_(CalledProcessError(1, ['ssh'])))
        vending_machine.left_group.led_color_with_time(255, 255, 255, 1000)
