from elephant_vending_machine.libraries.vending_machine import VendingMachine, SensorGrouping, LEFT_SCREEN
from time import sleep

def timeout_wait_for_detection(a):
    sleep(2)
    return LEFT_SCREEN

def test_wait_for_input(monkeypatch):
    monkeypatch.setattr('elephant_vending_machine.libraries.vending_machine.PiGPIOFactory', lambda *a, **k: None)
    monkeypatch.setattr('elephant_vending_machine.libraries.vending_machine.MotionSensor', lambda *a, **k: None)
    monkeypatch.setattr('elephant_vending_machine.libraries.vending_machine.LED', lambda *a, **k: None)
    monkeypatch.setattr('elephant_vending_machine.libraries.vending_machine.SensorGrouping.wait_for_detection', lambda a: LEFT_SCREEN)
    vending_machine = VendingMachine(['1','2','3'],[])
    result = vending_machine.wait_for_input([vending_machine.left_group, vending_machine.right_group], 5)
    assert result == 'left'

def test_wait_for_input_timeout(monkeypatch):
    monkeypatch.setattr('elephant_vending_machine.libraries.vending_machine.PiGPIOFactory', lambda *a, **k: None)
    monkeypatch.setattr('elephant_vending_machine.libraries.vending_machine.MotionSensor', lambda *a, **k: None)
    monkeypatch.setattr('elephant_vending_machine.libraries.vending_machine.LED', lambda *a, **k: None)
    monkeypatch.setattr('elephant_vending_machine.libraries.vending_machine.SensorGrouping.wait_for_detection', timeout_wait_for_detection)
    vending_machine = VendingMachine(['1','2','3'],[])
    result = vending_machine.wait_for_input([vending_machine.left_group, vending_machine.right_group], 1)
    assert result == 'timeout'