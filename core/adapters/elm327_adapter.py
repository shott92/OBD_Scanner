import obd
from ..hal.vci_interface import VCIInterface

class ELM327Adapter(VCIInterface):
    def __init__(self, port, config=None):
        super().__init__(config)
        self._port = port
        self._connection = None

    def connect(self) -> bool:
        try:
            self._connection = obd.OBD(self._port)
            self._is_connected = self._connection.is_connected()
            return self._is_connected
        except Exception:
            self._is_connected = False
            return False

    def disconnect(self):
        if self.is_connected:
            self._connection.close()
            self._connection = None
        self._is_connected = False

    def send_frame(self, data: bytes, protocol: str = "CAN", **kwargs):
        # ELM327 typically takes string commands or hex
        pass

    def read_frame(self, timeout: float = 0.1):
        return None

    def send_receive(self, command_name, command):
        """Legacy helper for existing UI"""
        if not self.is_connected:
            return "ERROR: Not connected"

        # 'command' here is expected to be an obd.commands object in the legacy code
        # We need to handle raw vs object if we change the flow, but staying compatible for now
        response = self._connection.query(command)

        if response.is_null():
            return "N/A"
        
        # Format response for display
        if isinstance(response.value, obd.UnitsAndMagnitudes.UnitQuantity):
            return f"{response.value.magnitude:.2f} {response.value.units}"
        elif isinstance(response.value, list) and len(response.value) > 0:
            return ", ".join([f"{item[0]} ({item[1]})" for item in response.value])
        else:
            return str(response.value)
