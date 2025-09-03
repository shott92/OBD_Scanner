from PyQt5.QtCore import QObject, pyqtSignal
import time

class CommunicationManager(QObject):
    """
    Manages communication with a vehicle adapter in a separate thread.
    """
    connection_status = pyqtSignal(bool, str)
    log_message = pyqtSignal(str)
    data_received = pyqtSignal(str, str)

    def __init__(self, adapter):
        super().__init__()
        self.adapter = adapter
        self._is_running = False

    def run(self):
        """
        The main worker method for the thread. Connects to the adapter
        and enters a loop to keep the thread alive for command execution.
        """
        self._is_running = True
        self.log_message.emit(f"INFO: Worker thread started. Attempting to connect...")

        try:
            if not self.adapter.connect():
                raise ConnectionError("Adapter failed to connect.")

            self.log_message.emit("SUCCESS: Connection established.")
            self.connection_status.emit(True, f"Connected via {self.adapter.get_type_string()}")

        except Exception as e:
            self.log_message.emit(f"ERROR: Failed to connect: {e}")
            self.connection_status.emit(False, "Connection Failed")
            self._is_running = False # Stop running if connection fails
            return

        # Keep the thread alive
        while self._is_running:
            time.sleep(0.1)

        self.log_message.emit("INFO: Worker thread finished.")

    def stop(self):
        """
        Stops the worker thread loop and disconnects the adapter.
        """
        self.log_message.emit("INFO: Stopping worker...")
        self._is_running = False
        if self.adapter:
            self.adapter.disconnect()
        self.log_message.emit("INFO: Disconnected.")

    def execute_command(self, cmd_name, command_obj, command_hex):
        """
        Executes a command using the connected adapter.
        """
        if not self.adapter or not self.adapter.is_connected:
            self.log_message.emit("ERROR: Not connected. Cannot send command.")
            return

        self.log_message.emit(f"TX: [{cmd_name}] - {command_hex or command_obj.name}")

        try:
            # The adapter's send_receive method will handle the different command types
            response = self.adapter.send_receive(cmd_name, command_obj, command_hex)
            self.log_message.emit(f"RX: {response}")
            self.data_received.emit(cmd_name, str(response))
        except Exception as e:
            self.log_message.emit(f"ERROR: Failed to execute command '{cmd_name}': {e}")
