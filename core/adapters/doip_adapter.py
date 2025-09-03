from .base_adapter import BaseAdapter
from doipclient import DoIPClient
from doipclient.connectors import DoIPClientUDSConnector
from udsoncan.client import Client
from udsoncan.configs import defaultConfig

class DoIPAdapter(BaseAdapter):
    def __init__(self, ip_address, logical_address):
        self._ip = ip_address
        self._addr = int(logical_address, 16) # Convert hex string to int
        self._client = None
        self._connection_open = False

    def connect(self):
        try:
            # Note: For real hardware, you may need to add error handling and timeouts
            connector = DoIPClientUDSConnector(DoIPClient(self._ip, self._addr))
            self._client = Client(connector, config=defaultConfig)
            self._client.open()
            self._connection_open = self._client.is_open()
            return self._connection_open
        except Exception:
            self._connection_open = False
            return False

    def disconnect(self):
        if self._client:
            self._client.close()
        self._connection_open = False

    @property
    def is_connected(self):
        return self._connection_open

    def send_receive(self, command_name, command_hex):
        if not self.is_connected:
            return "ERROR: Not connected"
        try:
            request_payload = bytes.fromhex(command_hex)
            response = self._client.send_receive(request_payload)
            if response.positive:
                return response.payload.hex()
            else:
                return f"Negative Response: {response.code_name}"
        except Exception as e:
            return f"Error: {e}"
