from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from .adapters.elm327_adapter import ELM327Adapter
from .adapters.doip_adapter import DoIPAdapter
# from .hal.j2534_wrapper import J2534Wrapper # Uncomment when J2534 is fully ready

class CommunicationManager(QObject):
    connection_status = pyqtSignal(bool, str)
    log_message = pyqtSignal(str)
    data_received = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.adapter = None
        self.tester_present_timer = QTimer()
        self.tester_present_timer.timeout.connect(self.send_tester_present)
        self.tester_present_enabled = False

    def connect_vehicle(self, config):
        """
        config: dict containing adapter configuration. 
        Example: {"adapter_type": "DoIP", "ip": "...", "address": "...", "target_address": "...", "tester_present": bool}
        """
        adapter_type = config.get("adapter_type")
        self.tester_present_enabled = config.get("tester_present", False)
        
        self.log_message.emit(f"INFO: Attempting to connect via {adapter_type}...")

        try:
            if adapter_type == "ELM327":
                self.adapter = ELM327Adapter(config.get("port"))
            elif adapter_type == "DoIP":
                # Pass target address if separate from gateway address
                self.adapter = DoIPAdapter(
                    config.get("ip"), 
                    config.get("address"), 
                    target_address=config.get("target_address")
                )
            elif adapter_type == "J2534":
                 self.log_message.emit("WARNING: J2534 support is experimental.")
                 # self.adapter = J2534Wrapper(config.get("dll_path"))
                 return
            else:
                self.log_message.emit("ERROR: Unknown adapter type selected.")
                return

            if self.adapter.connect():
                self.log_message.emit(f"SUCCESS: Connection established via {self.adapter.get_name()}.")
                self.connection_status.emit(True, f"Connected via {adapter_type}")
                
                if self.tester_present_enabled:
                    self.start_tester_present()
            else:
                raise ConnectionError("Adapter failed to connect.")
        except Exception as e:
            self.log_message.emit(f"ERROR: Failed to connect. {e}")
            self.connection_status.emit(False, "Connection Failed")
            self.adapter = None
            self.stop_tester_present()
    
    def disconnect_vehicle(self):
        self.stop_tester_present()
        if self.adapter:
            self.adapter.disconnect()
            self.adapter = None
        self.log_message.emit("INFO: Disconnected.")
        self.connection_status.emit(False, "Disconnected")

    def start_tester_present(self):
        self.log_message.emit("INFO: Starting Tester Present (2000ms).")
        self.tester_present_timer.start(2000)

    def stop_tester_present(self):
        if self.tester_present_timer.isActive():
            self.tester_present_timer.stop()
            self.log_message.emit("INFO: Stopped Tester Present.")

    def send_tester_present(self):
        if self.adapter and self.adapter.is_connected:
            # Tester Present: Service 3E, Sub-function 80 (Zero subfunction, Suppress Response)
            # This is a generic Keep-Alive.
            # Note: For DoIP/UDS adapter, we might need a specific call or raw frame.
            # Using execute_command logic for now, but suppressing log if possible?
            # Or better, use a lightweight send if the adapter supports it.
            try:
                # self.log_message.emit("TX: Tester Present ($3E 80)") # Optional: too verbose?
                if hasattr(self.adapter, 'send_receive'): 
                     # This might wait for response, which $80 suppresses...
                     # But for ELM327 usually you just send generic.
                     # Ideally we use send_frame.
                     pass
                # For now just logging to show it "fires"
                # self.log_message.emit("DEBUG: Tester Present tick")
                pass
            except Exception:
                pass

    def execute_command(self, cmd_name, cmd):
        if not self.adapter or not self.adapter.is_connected:
            self.log_message.emit("ERROR: Not connected. Cannot send command.")
            return

        self.log_message.emit(f"TX: [{cmd_name}]")
        
        # We need to bridge the gap between legacy UI command objects and the new HAL
        # For now, we rely on the adapter's implementation of send_receive (which we kept for compatibility)
        if hasattr(self.adapter, 'send_receive'):
            response = self.adapter.send_receive(cmd_name, cmd)
            self.log_message.emit(f"RX: {response}")
            self.data_received.emit(cmd_name, str(response))
        else:
             self.log_message.emit("ERROR: Adapter does not support legacy send_receive.")
             # Future: usage of send_frame / read_frame
