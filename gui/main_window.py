# gui/main_window.py
import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from PyQt5.QtCore import QThread, Qt
from PyQt5.QtGui import QIcon

from gui.widgets.connection_widget import ConnectionWidget
from gui.widgets.command_widget import CommandWidget, DEFAULT_COMMANDS_J1979
from gui.widgets.data_view_widget import DataViewWidget
from gui.widgets.log_widget import LogWidget

from core.communication_manager import CommunicationManager
from core.adapters.elm327_adapter import ELM327Adapter
from core.adapters.doip_adapter import DoIPAdapter

APP_TITLE = "Gemini OBD-II Diagnostic Tool"
APP_VERSION = "2.0 (Multi-Adapter)"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_TITLE} v{APP_VERSION}")
        self.setGeometry(100, 100, 1200, 700)
        self.set_icon()

        self.comm_thread = None
        self.comm_worker = None

        self.init_ui()
        self.apply_stylesheet()

    def init_ui(self):
        # --- Create Widgets ---
        self.connection_widget = ConnectionWidget()
        self.command_widget = CommandWidget()
        self.data_view_widget = DataViewWidget()
        self.log_widget = LogWidget()
        
        self.data_view_widget.populate_initial_data(DEFAULT_COMMANDS_J1979.keys())

        # --- Layout ---
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        left_column = self.connection_widget
        center_column = self.command_widget
        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        right_layout.addWidget(self.data_view_widget, 1) # 1 stretch factor
        right_layout.addWidget(self.log_widget, 1)     # 1 stretch factor
        
        main_layout.addWidget(left_column)
        main_layout.addWidget(center_column)
        main_layout.addWidget(right_column, 1) # Make right column stretch

        # --- Connect Signals ---
        self.connection_widget.connect_clicked.connect(self.start_connection)
        self.connection_widget.disconnect_clicked.connect(self.stop_connection)
        self.command_widget.command_triggered.connect(self.on_command_triggered)

    def start_connection(self, config):
        self.log_widget.add_log(f"INFO: Received connect request with config: {config}")
        
        adapter = None
        try:
            if config['type'] == 'ELM327 (Serial)':
                if "No ports" in config['port']:
                    self.log_widget.add_log("ERROR: No serial port selected.")
                    return
                adapter = ELM327Adapter(port=config['port'])
            
            elif config['type'] == 'DoIP (Ethernet)':
                adapter = DoIPAdapter(vehicle_ip=config['ip'], ecu_addr=config['address'])
            
            else:
                self.log_widget.add_log(f"ERROR: Unknown adapter type '{config['type']}'")
                return
        except Exception as e:
            self.log_widget.add_log(f"ERROR: Failed to initialize adapter: {e}")
            return

        self.connection_widget.set_status(False, "Connecting...")
        
        # Setup worker and thread
        self.comm_thread = QThread()
        self.comm_worker = CommunicationManager(adapter)
        self.comm_worker.moveToThread(self.comm_thread)

        # Connect worker signals to GUI slots
        self.comm_thread.started.connect(self.comm_worker.run)
        self.comm_worker.connection_status.connect(self.on_connection_status)
        self.comm_worker.log_message.connect(self.log_widget.add_log)
        self.comm_worker.data_received.connect(self.data_view_widget.update_data)

        self.comm_thread.start()

    def stop_connection(self):
        if self.comm_worker:
            self.comm_worker.stop()
        if self.comm_thread:
            self.comm_thread.quit()
            self.comm_thread.wait(2000) # Wait 2s for graceful shutdown
        self.on_connection_status(False, "Disconnected")

    def on_connection_status(self, is_connected, message):
        self.connection_widget.set_status(is_connected, message)

    def on_command_triggered(self, name, command_obj, command_hex):
        if self.comm_worker:
            self.comm_worker.execute_command(name, command_obj, command_hex)
        else:
            self.log_widget.add_log("ERROR: Not connected. Cannot send command.")

    def apply_stylesheet(self):
        style_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'style', 'stylesheet.qss')
        try:
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Stylesheet not found.")

    def set_icon(self):
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icons', 'app_icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def closeEvent(self, event):
        """Ensure the communication thread is cleaned up on exit."""
        self.stop_connection()
        event.accept()
