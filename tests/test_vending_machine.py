from elephant_vending_machine.libraries.vending_machine import VendingMachine, SensorGrouping

def test_wait_for_input(monkeypatch):
    monkeypatch.setattr('elephant_vending_machine.libraries.vending_machine.SensorGrouping.wait_for_detection', lambda: 9)
    vending_machine = VendingMachine(['1','2','3'])
    sensor_grouping = vending_machine.left_group
    assert vending_machine.wait_for_input() == 9
