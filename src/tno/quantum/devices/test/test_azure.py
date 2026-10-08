import logging
from typing import Any

import pennylane as qml
import pytest

from tno.quantum.devices import DeviceConfig, azure


def can_connect_to_azure() -> bool:
    try:
        azure.connect()
    except Exception:  # noqa: BLE001
        return False
    return True


_CAN_CONNECT_TO_AZURE = can_connect_to_azure()


@pytest.mark.skipif(
    not _CAN_CONNECT_TO_AZURE, reason="Could not connect to Azure service"
)
def test_azure_bell_circuit() -> None:
    """Test if a Bell circuit can be run on one of Azure's backends."""
    # Find a simulator backend
    backend_name = next((name for name in azure.backends() if "sim" in name), None)

    if backend_name is None:
        msg = (
            "Could not perform test `test_azure_bell_circuit`, "
            "because no Azure simulator backend was found."
        )
        logging.warning(msg)  # noqa: LOG015
        return

    # Construct device via DeviceConfig
    dev = DeviceConfig(
        "azure.remote", options={"backend_name": backend_name, "wires": 2}
    ).get_instance()

    # Create and execute a quantum circuit on the defined device
    @qml.qnode(dev, shots=100)  # type: ignore[untyped-decorator]
    def circuit() -> Any:
        qml.Hadamard(0)
        qml.CNOT([0, 1])
        return qml.sample()

    circuit()
