"""This module contains the ``DeviceConfig`` class."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from functools import partial
from typing import Any

import pennylane as qml
from pennylane.devices import Device
from tno.quantum.utils import BaseConfig


class DeviceConfig(BaseConfig[Device]):
    """Configuration class for creating PennyLane :py:class:`~pennylane.devices.Device`
    instances.

    Supported devices can be obtained by calling
    :py:meth:`~DeviceConfig.supported_items`.

    Example:
        >>> from tno.quantum.devices import DeviceConfig
        >>>
        >>> # List available PennyLane devices
        >>> sorted(DeviceConfig.supported_items())  # doctest: +ELLIPSIS
        [..., 'default.gaussian', 'default.mixed', 'default.qubit', ...]
        >>>
        >>> # Instantiate PennyLane device
        >>> config = DeviceConfig("default.qubit", options={"wires": 5})
        >>> type(config.get_instance())
        <class 'pennylane.devices.default_qubit.DefaultQubit'>
    """  # noqa: D205

    def __init__(
        self,
        name: str,
        options: Mapping[str, Any] | None = None,
    ) -> None:
        """Initialize :py:class:`DeviceConfig`.

        Args:
            name: Name of the PennyLane :py:class:`~pennylane.devices.Device`.
            options: Keyword arguments to pass to the device.
        """
        super().__init__(name=name, options=options)

    @staticmethod
    def supported_items() -> dict[str, Callable[..., Device]]:
        """Obtain all supported PennyLane backend devices.

        Returns:
            Dictionary with callable that instantiate Pennylane Device instances.
        """
        return {name: partial(qml.device, name=name) for name in qml.plugin_devices}

    def get_instance(self, *args: Any, **kwargs: Any) -> Device:
        """Instantiate PennyLane :py:class:`~pennylane.devices.Device`.

        Args:
            args: Additional positional arguments to pass to the device.
            kwargs: Additional keyword arguments to pass to the device.
        """
        return super().get_instance(*args, **kwargs)
