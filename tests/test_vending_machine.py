from elephant_vending_machine.libraries.vending_machine import VendingMachine

def test_wait_for_input(monkeypatch):
    monkeypatch.setattr('elephant_vending_machine.libraries.vending_machine.VendingMachine.SensorGrouping.wait_for_detection', lambda: 9)
    VendingMachine = new VendingMachine(['1','2','3'])
    assert VendingMachine.wait_for_input() == 9
