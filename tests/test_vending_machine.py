from elephant_vending_machine.libraries.vending_machine import VendingMachine, SensorGrouping, LEFT_SCREEN
import pytest
import time


class MockController:
    def getPosition(self, x):
        return 0


def timeout_wait_for_detection(a):
    time.sleep(2)
    return LEFT_SCREEN


def test_wait_for_input(monkeypatch):
    monkeypatch.setattr(
        'elephant_vending_machine.libraries.vending_machine.SensorGrouping.wait_for_detection', lambda a: LEFT_SCREEN)
    vending_machine = VendingMachine(['1', '2', '3'], {})
    result = vending_machine.wait_for_input(
        [vending_machine.left_group, vending_machine.right_group], 5)
    assert result == 'left'


def test_wait_for_input_timeout(monkeypatch):
    monkeypatch.setattr(
        'elephant_vending_machine.libraries.vending_machine.SensorGrouping.wait_for_detection', timeout_wait_for_detection)
    vending_machine = VendingMachine(['1', '2', '3'], {})
    result = vending_machine.wait_for_input(
        [vending_machine.left_group, vending_machine.right_group], 1)
    assert result == 'timeout'


def test_wait_for_detection(monkeypatch):
    monkeypatch.setattr('maestro.Controller.getPosition', lambda input: 0)
    vending_machine = VendingMachine(['1', '2', '3'], {})
    result = vending_machine.wait_for_input(
        [vending_machine.left_group, vending_machine.right_group], 5)
    assert result in ['left', 'right']


@pytest.mark.skip(reason="There is no good way to unit test an ssh connection and visual display with pytest.")
def test_display(monkeypatch):
    vending_machine = VendingMachine(['192.168.1.35', '2', '3'], {
                                     'REMOTE_IMAGE_DIRECTORY': '/home/pi/elephant_vending_machine/images'})
    vending_machine.left_group.display_on_screen('elephant.jpg', True)
    time.sleep(3)
    vending_machine.left_group.display_on_screen('elephant2.jpg', True)
    assert type(
        vending_machine.left_group.pid_of_previous_display_command) is int
