# TNO Quantum: Devices

TNO Quantum provides generic software components aimed at facilitating the development
of quantum applications.

The devices package provides a consistent way to configure and instantiate PennyLane devices,
including local devices and remote backends from IBM Quantum Platform and Azure Quantum.

## Documentation

Documentation of the `tno.quantum.optimization.qubo.components` package can be found [here](https://tno-quantum.github.io/documentation/).


## Usage

The `tno.quantum.devices` package can be used as shown in the following example.

```python
from tno.quantum.devices import DeviceConfig

# Get a list of supported items
sorted(DeviceConfig.supported_items())
# ['default.clifford', 'default.gaussian', 'default.mixed', ...]

# Create a device
config = DeviceConfig("default.qubit", options={"wires": 5})
config.get_instance()
# <default.qubit device (wires=5) at 0x7b9fd6fc7770>

# Create an IBM device using "ibm.remote"
config = DeviceConfig("ibm.remote", options={"backend_name": "ibm_aachen", "wires": 5})
config.get_instance()
# <IBMDevice device (wires=5) at 0x7b9ffcfa5f30>

# Create an Azure device using "azure.remote"
config = DeviceConfig(
    "azure.remote", options={"backend_name": "rigetti_cepheus", "wires": 5}
)
config.get_instance()
# <AzureDevice device (wires=5) at 0x7b9fdcbba9e0>
```

## (End)use limitations

The content of this software may solely be used for applications that comply with international export control laws.
