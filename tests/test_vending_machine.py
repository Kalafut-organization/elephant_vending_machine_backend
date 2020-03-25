from elephant_vending_machine.libraries.vending_machine import VendingMachine, SensorGrouping, LEFT_SCREEN
import pytest
import time


def timeout_wait_for_detection(a):
    time.sleep(2)
    return LEFT_SCREEN


def test_wait_for_input(monkeypatch):
    monkeypatch.setattr(
        'elephant_vending_machine.libraries.vending_machine.PiGPIOFactory', lambda *a, **k: None)
    monkeypatch.setattr(
        'elephant_vending_machine.libraries.vending_machine.MotionSensor', lambda *a, **k: None)
    monkeypatch.setattr(
        'elephant_vending_machine.libraries.vending_machine.LED', lambda *a, **k: None)
    monkeypatch.setattr(
        'elephant_vending_machine.libraries.vending_machine.SensorGrouping.wait_for_detection', lambda a: LEFT_SCREEN)
    vending_machine = VendingMachine(['1', '2', '3'], {})
    result = vending_machine.wait_for_input(
        [vending_machine.left_group, vending_machine.right_group], 5)
    assert result == 'left'


def test_wait_for_input_timeout(monkeypatch):
    monkeypatch.setattr(
        'elephant_vending_machine.libraries.vending_machine.PiGPIOFactory', lambda *a, **k: None)
    monkeypatch.setattr(
        'elephant_vending_machine.libraries.vending_machine.MotionSensor', lambda *a, **k: None)
    monkeypatch.setattr(
        'elephant_vending_machine.libraries.vending_machine.LED', lambda *a, **k: None)
    monkeypatch.setattr(
        'elephant_vending_machine.libraries.vending_machine.SensorGrouping.wait_for_detection', timeout_wait_for_detection)
    vending_machine = VendingMachine(['1', '2', '3'], {})
    result = vending_machine.wait_for_input(
        [vending_machine.left_group, vending_machine.right_group], 1)
    assert result == 'timeout'

@pytest.mark.skip(reason="There is no good way to unit test an ssh connection and visual display with pytest.")
def test_display(monkeypatch):
    monkeypatch.setattr(
        'elephant_vending_machine.libraries.vending_machine.PiGPIOFactory', lambda *a, **k: None)
    monkeypatch.setattr(
        'elephant_vending_machine.libraries.vending_machine.MotionSensor', lambda *a, **k: None)
    monkeypatch.setattr(
        'elephant_vending_machine.libraries.vending_machine.LED', lambda *a, **k: None)
    vending_machine = VendingMachine(['192.168.1.35', '2', '3'], {
                                     'REMOTE_IMAGE_DIRECTORY': '/home/pi/elephant_vending_machine/images'})
    vending_machine.left_group.display_on_screen('elephant.jpg', True)
    time.sleep(3)
    vending_machine.left_group.display_on_screen('elephant2.jpg', True)
    assert type(
        vending_machine.left_group.pid_of_previous_display_command) is int

@pytest.mark.skip(reason="There is no good way to unit test an ssh connection and LED display with pytest.")
def test_LED_strips(monkeypatch):
    monkeypatch.setattr(
        'elephant_vending_machine.libraries.vending_machine.PiGPIOFactory', lambda *a, **k: None)
    monkeypatch.setattr(
        'elephant_vending_machine.libraries.vending_machine.MotionSensor', lambda *a, **k: None)
    monkeypatch.setattr(
        'elephant_vending_machine.libraries.vending_machine.LED', lambda *a, **k: None)
    vending_machine = VendingMachine(['192.168.1.35', '2', '3'], {
                                     'REMOTE_IMAGE_DIRECTORY': '/home/pi/elephant_vending_machine/images', 'REMOTE_LED_SCRIPT_DIRECTORY': '/home/pi/rpi_ws281x/python'})
    vending_machine.left_group.change_led('green')
