from PyQt5.QtCore import QObject, pyqtSignal
from .adapters.elm327_adapter import ELM327Adapter
from .adapters.doip_adapter import DoIPAdapter

class CommunicationManager(QObject):
    connection_status = pyqtSignal(bool, str)
    log_message = pyqtSignal(str)
    data_received = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.adapter = None

    def connect_vehicle(self, config):
        adapter_type = config.get("adapter_type")
        self.log_message.emit(f"INFO: Attempting to connect via {adapter_type}...")

        try:
            if adapter_type == "ELM327":
                self.adapter = ELM327Adapter(config.get("port"))
            elif adapter_type == "DoIP":
                self.adapter = DoIPAdapter(config.get("ip"), config.get("address"))
            else:
                self.log_message.emit("ERROR: Unknown adapter type selected.")
                return

            if self.adapter.connect():
                self.log_message.emit(f"SUCCESS: Connection established.")
                self.connection_status.emit(True, f"Connected via {adapter_type}")
            else:
                raise ConnectionError("Adapter failed to connect.")
        except Exception as e:
            self.log_message.emit(f"ERROR: Failed to connect. {e}")
            self.connection_status.emit(False, "Connection Failed")
            self.adapter = None
    
    def disconnect_vehicle(self):
        if self.adapter:
            self.adapter.disconnect()
            self.adapter = None
        self.log_message.emit("INFO: Disconnected.")
        self.connection_status.emit(False, "Disconnected")

    def execute_command(self, cmd_name, cmd):
        if not self.adapter or not self.adapter.is_connected:
            self.log_message.emit("ERROR: Not connected. Cannot send command.")
            return

        self.log_message.emit(f"TX: [{cmd_name}]")
        
        # ELM327 commands are objects, DoIP commands are hex strings
        response = self.adapter.send_receive(cmd_name, cmd)
        
        self.log_message.emit(f"RX: {response}")
        self.data_received.emit(cmd_name, str(response))
