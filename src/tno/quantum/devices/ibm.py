"""This module contains functionality related to the IBM quantum provider.

The :py:class:`IBMDevice` class defines a PennyLane device (called ``ibm.remote``)
which can be used execute circuits on the IBM backends.
The following example shows how this can be done.

Example:
-------

.. code-block:: python

    # To use any of the IBM backends, make sure your account is saved.
    # This method stores the account to disk, so it only needs to run once.
    from tno.quantum.devices import ibm

    ibm.save_account(
        token="...",
        instance="...",
    )

    # An IBM device can be constructed in two ways.
    # (1) Either directly using `qml.device`
    import pennylane as qml

    dev = qml.device("ibm.remote", backend_name="ibm_strasbourg", wires=2)

    # (2) Using the `DeviceConfig` class.
    from tno.quantum.devices import DeviceConfig

    config = DeviceConfig(
        "ibm.remote",
        options={"backend_name": "ibm_strasbourg", "wires": 2},
    )
    dev = config.get_instance()

    # Now, we can create and execute a quantum circuit on the defined device.
    @qml.qnode(dev, shots=100)
    def circuit():
        qml.Hadamard(0)
        qml.CNOT([0, 1])
        return qml.sample()

    samples = circuit()
"""

import importlib.util
from typing import Any, Literal, cast

from pennylane.devices import ExecutionConfig
from pennylane.tape import QuantumScriptOrBatch
from pennylane.typing import Result, ResultBatch
from pennylane.wires import WiresLike
from pennylane_qiskit.remote import RemoteDevice


def _is_ibm_installed() -> bool:
    return importlib.util.find_spec("qiskit_ibm_runtime") is not None


if _is_ibm_installed():
    from qiskit_ibm_runtime import QiskitRuntimeService
    from qiskit_ibm_runtime.ibm_backend import IBMBackend

_IBM_SERVICE: QiskitRuntimeService | None = None
_IBM_NOT_INSTALLED_MSG = (
    "because IBM quantum packages are not installed. "
    "These can be installed via `tno.quantum.devices[ibm]`."
)


def backends() -> list[str]:
    """Return a list of names of all available IBM devices."""
    global _IBM_SERVICE  # noqa: PLW0602
    connect()
    return [backend.name for backend in _IBM_SERVICE.backends()]  # type: ignore[union-attr]


def backend(name: str) -> IBMBackend:
    """Get IBM backend by name.

    Args:
        name: Name of the IBM backend.
    """
    global _IBM_SERVICE  # noqa: PLW0602
    connect()
    return cast("IBMBackend", _IBM_SERVICE.backend(name))  # type: ignore[union-attr]


def connect() -> None:
    """Connect to the IBM service.

    Before calling this method, an IBM account must be saved, e.g. using
    :py:meth:`save_account`. Otherwise, an exception will be raised.

    Raises:
        RuntimeError - If no IBM account is saved.s
    """
    global _IBM_SERVICE  # noqa: PLW0603

    if not _is_ibm_installed():
        msg = "Could not connect to IBM service, " + _IBM_NOT_INSTALLED_MSG
        raise RuntimeError(msg)

    if _IBM_SERVICE is None:
        _IBM_SERVICE = QiskitRuntimeService()


def save_account(  # noqa: PLR0913
    *,
    token: str,
    instance: str,
    channel: Literal["ibm_quantum_platform", "ibm_cloud"] = "ibm_quantum_platform",
    name: str | None = None,
    set_as_default: bool = True,
    overwrite: bool = False,
) -> None:
    """Save IBM account.

    Args:
        token: IBM Cloud API key.
        instance: This is a parameter to specify the CRN  or service name.
        channel: Channel type, either ``ibm_cloud`` or ``ibm_quantum_platform``.
        name: Name of the account to save.
        set_as_default: If :py:const:`True`, the account is saved as the default
            account.
        overwrite: If :py:const:`True`, the existing account is to be overwritten.
    """
    if not _is_ibm_installed():
        msg = "Failed to save IBM account, " + _IBM_NOT_INSTALLED_MSG
        raise RuntimeError(msg)

    QiskitRuntimeService.save_account(
        token=token,
        instance=instance,
        channel=channel,
        name=name,
        set_as_default=set_as_default,
        overwrite=overwrite,
    )


class IBMDevice(RemoteDevice):  # type: ignore[misc]
    """PennyLane device for IBM backends.

    This device can be constructed using :py:obj:`qml.device("ibm.remote", ...)`.
    """

    def __init__(self, *, backend_name: str, wires: WiresLike, **kwargs: Any) -> None:
        """Initialize IBM device.

        Args:
            backend_name: Name of the IBM backend.
            wires: Wires.
            kwargs: Additional keyword arguments to be passed to the underlying
                :py:class:`~pennylane_qiskit.remote.RemoteDevice`.
        """
        if not _is_ibm_installed():
            msg = "Failed to instantiate device 'ibm.remote', " + _IBM_NOT_INSTALLED_MSG
            raise RuntimeError(msg)

        self._backend_name = backend_name
        self._backend = backend(backend_name)
        super().__init__(backend=self._backend, wires=wires, **kwargs)

    def execute(
        self,
        circuits: QuantumScriptOrBatch,
        execution_config: ExecutionConfig | None = None,
    ) -> Result | ResultBatch:
        """Execute circuits with execution config."""
        return super().execute(circuits, execution_config)
