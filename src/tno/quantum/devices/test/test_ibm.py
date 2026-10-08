import logging
from typing import Any

import pennylane as qml
import pytest

from tno.quantum.devices import DeviceConfig, ibm


def can_connect_to_ibm() -> bool:
    try:
        ibm.connect()
    except Exception:  # noqa: BLE001
        return False
    return True


_CAN_CONNECT_TO_IBM = can_connect_to_ibm()


@pytest.mark.skipif(not _CAN_CONNECT_TO_IBM, reason="Could not connect to IBM service")
def test_ibm_bell_circuit() -> None:
    """Test if a Bell circuit can be run on one of IBM's backends."""
    # Find a simulator backend
    backend_name = next((name for name in ibm.backends() if "sim" in name), None)

    if backend_name is None:
        msg = (
            "Could not perform test `test_ibm_bell_circuit`, "
            "because no IBM simulator backend was found."
        )
        logging.warning(msg)  # noqa: LOG015
        return

    # Construct device via DeviceConfig
    dev = DeviceConfig(
        "ibm.remote", options={"backend_name": backend_name, "wires": 2}
    ).get_instance()

    # Create and execute a quantum circuit on the defined device
    @qml.qnode(dev, shots=100)  # type: ignore[untyped-decorator]
    def circuit() -> Any:
        qml.Hadamard(0)
        qml.CNOT([0, 1])
        return qml.sample()

    circuit()
