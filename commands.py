import obd

# These commands are compatible with the python-obd library for ELM327
ELM327_J1979_COMMANDS = {
    "Read RPM": obd.commands.RPM,
    "Read Vehicle Speed": obd.commands.SPEED,
    "Read Coolant Temp": obd.commands.COOLANT_TEMP,
    "Get DTCs": obd.commands.GET_DTC,
}

# These are raw UDS commands (hex strings) that can be sent over DoIP or ELM327
UDS_COMMANDS = {
    "Read VIN": "22F190",
    "Read ECU Serial": "22F18C",
    "Tester Present": "3E00",
}```

---

### `core/adapters/base_adapter.py`

This is an abstract base class that defines the "contract" for all adapters. Any new adapter (e.g., for Bluetooth) must have these methods.

```python
from abc import ABC, abstractmethod

class BaseAdapter(ABC):
    """
    Abstract Base Class for all communication adapters.
    Ensures that all adapters have a consistent interface.
    """
    @abstractmethod
    def connect(self):
        """Establishes a connection to the vehicle/adapter. Returns True on success."""
        pass

    @abstractmethod
    def disconnect(self):
        """Closes the connection."""
        pass

    @abstractmethod
    def send_receive(self, command_name, command):
        """Sends a command and returns the response."""
        pass

    @property
    @abstractmethod
    def is_connected(self):
        """Returns True if the connection is active."""
        pass
