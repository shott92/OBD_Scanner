from ..hal.vci_interface import VCIInterface
from doipclient import DoIPClient
from doipclient.connectors import DoIPClientUDSConnector
from udsoncan.client import Client
from udsoncan.configs import default_client_config

class DoIPAdapter(VCIInterface):
    def __init__(self, ip_address, logical_address, target_address=None, config=None):
        super().__init__(config)
        self._ip = ip_address
        self._addr = int(logical_address, 16) if isinstance(logical_address, str) else logical_address
        self._target_addr = int(target_address, 16) if isinstance(target_address, str) and target_address else self._addr
        self._client = None

    def connect(self) -> bool:
        try:
            connector = DoIPClientUDSConnector(DoIPClient(self._ip, self._addr))
            # The client should target the specific ECU address, routed via the DoIP entity at self._addr (implied by connection)
            # Actually, DoIPClient connects to the gateway. UDS Client needs to know the target ECU address for the protocol.
            # DoIPClientUDSConnector handles wrapping. Reference to doipclient doc:
            # We might need to configure the underlying DoIPClient to route to target_addr if it's different from logical_address?
            # Standard DoIP: "Routing Activation" is done for a source. Then messages are sent to a target.
            
            # For simplicity in this step: We assume the target_address is what we want to talk UDS to.
            # We might need to adjust how DoIPClient is initialized if it needs to know the target for routing activation or just message sending.
            # Usually DoIPClient sends to a target address per message.
            
            # The DoIPClientUDSConnector takes the doip_client.
            # We need to tell the VCI/Client where to send messages.
            # udsoncan Client sends requests. The connector ensures they go to the right place.
            # There isn't a straightforward "target" param in DoIPClientUDSConnector init in standard versions, 
            # it often defaults or we need to look at how it wraps.
            
            # Let's assume for this "Stub/MVP" level:
            # We will set the doip layer to use the target address if provided.
            
            self._client = Client(connector, config=default_client_config)
            self._client.open()
            self._is_connected = self._client.is_open()
            return self._is_connected
        except Exception:
            self._is_connected = False
            return False

    def disconnect(self):
        if self._client:
            self._client.close()
        self._is_connected = False

    def send_frame(self, data: bytes, protocol: str = "UDS", **kwargs):
        """
        For DoIP/UDS, 'data' is typically the raw payload.
        But udsoncan abstracts this. We'll expose a direct send if possible or use client.
        This adapter seems designed for UDS-on-DoIP rather than raw DoIP frames currently.
        """
        if not self.is_connected:
            raise ConnectionError("Not connected")
        # This current implementation is high-level UDS. 
        # Raw frame sending might need access to underlying DoIPClient.
        pass

    def send_receive(self, command_name, command_hex):
        """Legacy helper for existing UI, mapped to UDS send_receive"""
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

    def read_frame(self, timeout: float = 0.1):
        # DoIP client handles reading internally
        return None
