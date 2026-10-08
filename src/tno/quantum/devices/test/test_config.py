"""Test module for the DeviceConfig class."""

from pennylane.devices.default_qubit import DefaultQubit

from tno.quantum.devices import DeviceConfig


def test_device_config_contains_custom_devices() -> None:
    """Test that the DeviceConfig contains the custom IBM and Azure devices."""
    items = DeviceConfig.supported_items()
    assert "ibm.remote" in items
    assert "azure.remote" in items


def test_device_config_instantiate_default_qubit() -> None:
    """Test that the DeviceConfig can properly instantiate PennyLane devices."""
    config = DeviceConfig("default.qubit", options={"wires": 1})
    dev = config.get_instance()
    assert isinstance(dev, DefaultQubit)
