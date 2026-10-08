"""This package can be used to connect to backends from various quantum providers.

Currently, the supported quantum providers are:

- `IBM Quantum Platform <https://quantum.cloud.ibm.com/>`_
- `Azure Quantum <https://azure.microsoft.com/en-us/solutions/quantum-computing>`_

Besides external quantum providers, this package also provides the functionality to
instantiate the default PennyLane devices.


Installation
------------

Install the base package using ``pip``:

.. code-block:: bash

    pip install tno.quantum.devices

Provider-specific dependencies can be installed via extras:

.. code-block:: bash

    pip install tno.quantum.devices[ibm]    # for IBM Quantum backends
    pip install tno.quantum.devices[azure]   # for Azure Quantum backends

"""

from tno.quantum.devices._config import DeviceConfig

__all__ = ["DeviceConfig"]

__version__ = "1.0.1"
