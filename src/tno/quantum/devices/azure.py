"""This module contains functionality related to the Azure quantum provider.

The :py:class:`AzureDevice` class defines a PennyLane device (called ``azure.remote``)
which can be used execute circuits on the Azure backends.
The following example shows how this can be done.

Example:
-------

.. code-block:: python

    # To use any of the Azure backends, make sure your connection string is set.
    # This method sets the connection string in the environment variables, so it needs
    # to be set at the start of every session.
    from tno.quantum.devices import azure

    azure.set_connection_string(
        connection_string="...",
    )

    # An Azure device can be constructed in two ways.
    # (1) Either directly using `qml.device`
    import pennylane as qml

    dev = qml.device("azure.remote", backend_name="quantinuum.sim.h2-1e", wires=2)

    # (2) Using the `DeviceConfig` class.
    from tno.quantum.devices import DeviceConfig

    config = DeviceConfig(
        "azure.remote",
        options={"backend_name": "quantinuum.sim.h2-1e", "wires": 2},
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

from __future__ import annotations

import importlib.util
import os
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, cast

from pennylane_qiskit.remote import RemoteDevice

if TYPE_CHECKING:
    from pennylane.devices import ExecutionConfig
    from pennylane.tape import QuantumScriptOrBatch
    from pennylane.typing import Result, ResultBatch
    from pennylane.wires import WiresLike
    from qiskit import QuantumCircuit
    from qiskit.circuit import Instruction


def _is_azure_installed() -> bool:
    return importlib.util.find_spec("azure") is not None


if _is_azure_installed():
    from azure.quantum import Workspace
    from azure.quantum.qiskit import AzureQuantumProvider
    from azure.quantum.qiskit.backends.backend import AzureBackendConfig

    if TYPE_CHECKING:
        from azure.quantum.qiskit.backends import AzureBackendBase

    # Ad-hoc fix for `azure-quantum` bug

    def azure_backend_config_getattr_fixed(  # noqa: D103
        self: AzureBackendConfig, name: str
    ) -> Any:
        if name == "max_experiments":
            return 1
        try:
            return self.__dict__[name]
        except KeyError as exc:
            if name == "metadata":
                msg = "AzureBackendConfig has no property `metadata`"
                raise AttributeError(msg) from None
            if name in self.metadata:
                return self.metadata[name]
            msg = f"'{type(self).__name__}' object has no attribute '{name}'"
            raise AttributeError(msg) from exc

    AzureBackendConfig.__getattr__ = azure_backend_config_getattr_fixed


_AZURE_SERVICE: AzureQuantumProvider | None = None
_AZURE_QUANTUM_CONNECTION_STRING = "AZURE_QUANTUM_CONNECTION_STRING"
_AZURE_NOT_INSTALLED_MSG = (
    "because Azure quantum packages are not installed. "
    "These can be installed via `tno.quantum.devices[azure]`."
)


def backends() -> list[str]:
    """Returns a list of names of all available Azure backends."""
    global _AZURE_SERVICE  # noqa: PLW0602
    connect()
    return [backend.name for backend in _AZURE_SERVICE.backends()]  # type: ignore[union-attr]


def backend(name: str) -> AzureBackendBase:
    """Get Azure backend by name.

    Args:
        name: Name of the Azure backend.
    """
    global _AZURE_SERVICE  # noqa: PLW0602
    connect()
    return cast("AzureBackendBase", _AZURE_SERVICE.get_backend(name))  # type: ignore[union-attr]


def connect() -> None:
    """Connect to the Azure service.

    Before calling this method, a connection string must be set as an environment
    variable, e.g. using :py:meth:`set_connection_string`. Otherwise, an exception
    will be raised.

    Raises:
        RuntimeError - If no connection string is set.
    """
    global _AZURE_SERVICE  # noqa: PLW0603

    if not _is_azure_installed():
        msg = "Could not connect to Azure service, " + _AZURE_NOT_INSTALLED_MSG
        raise RuntimeError(msg)

    if _AZURE_SERVICE is None:
        connection_string = os.environ.get(_AZURE_QUANTUM_CONNECTION_STRING, None)
        if connection_string is None:
            msg = (
                "No connection string found. "
                "Use `tno.quantum.devices.azure.set_connection_string` "
                "to set the connection string."
            )
            raise RuntimeError(msg)
        workspace = Workspace.from_connection_string(connection_string)
        _AZURE_SERVICE = AzureQuantumProvider(workspace)


def set_connection_string(
    connection_string: str,
) -> None:
    """Set the ``AZURE_QUANTUM_CONNECTION_STRING`` environment variable.

    Args:
        connection_string: Azure connection string.
    """
    os.environ[_AZURE_QUANTUM_CONNECTION_STRING] = connection_string


class AzureDevice(RemoteDevice):  # type: ignore[misc]
    """PennyLane device for Azure backends.

    This device can be constructed using :py:obj:`qml.device("azure.remote", ...)`.
    """

    def __init__(self, *, backend_name: str, wires: WiresLike, **kwargs: Any) -> None:
        """Initialize Azure device.

        Args:
            backend_name: Name of the Azure backend.
            wires: Wires.
            kwargs: Additional keyword arguments to be passed to the underlying
                :py:class:`~pennylane_qiskit.remote.RemoteDevice`.
        """
        if not _is_azure_installed():
            msg = (
                "Failed to instantiate device 'azure.remote', "
                + _AZURE_NOT_INSTALLED_MSG
            )
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

    def compile_circuits(self, circuits: list[QuantumCircuit]) -> list[QuantumCircuit]:
        """Compiles multiple circuits one after the other.

        Args:
            circuits: List of circuits to compile.

        Returns:
             List of compiled circuits
        """
        circuits = cast("list[QuantumCircuit]", super().compile_circuits(circuits))
        for circuit in circuits:
            self._remove_barriers(circuit)
        return circuits

    def _remove_barriers(self, circuit: QuantumCircuit) -> None:
        circuit.data = [
            instruction
            for instruction in cast("Iterable[Any]", circuit.data)
            if cast("Instruction", instruction.operation).name != "barrier"
        ]
