import obd
from .base_adapter import BaseAdapter

class ELM327Adapter(BaseAdapter):
    def __init__(self, port):
        self._port = port
        self._connection = None

    def connect(self):
        try:
            self._connection = obd.OBD(self._port)
            return self._connection.is_connected()
        except Exception:
            return False

    def disconnect(self):
        if self.is_connected:
            self._connection.close()
            self._connection = None

    @property
    def is_connected(self):
        return self._connection and self._connection.is_connected()

    def send_receive(self, command_name, command_obj, command_hex):
        if not self.is_connected:
            return "ERROR: Not connected"

        # ELM327 adapter uses the command object
        if not command_obj:
            return "ERROR: ELM327 requires a command object, but none was provided."

        response = self._connection.query(command_obj)

        if response.is_null():
            return "N/A"

        # Format response for display
        if isinstance(response.value, obd.UnitsAndMagnitudes.UnitQuantity):
            return f"{response.value.magnitude:.2f} {response.value.units}"
        elif isinstance(response.value, list) and len(response.value) > 0:
            # Handle list of DTCs
            return ", ".join([f"{item[0]} ({item[1]})" for item in response.value])
        else:
            return str(response.value)

    def get_type_string(self):
        return "ELM327"
