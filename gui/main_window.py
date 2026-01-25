# gui/main_window.py
import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QAction, QMenuBar, QFileDialog, QTabWidget
from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from gui.widgets.connection_widget import ConnectionWidget
from gui.widgets.command_widget import CommandWidget, DEFAULT_COMMANDS_J1979
from gui.widgets.data_view_widget import DataViewWidget
from gui.widgets.log_widget import LogWidget
from gui.widgets.dashboard_widget import DashboardWidget
from gui.widgets.repo_widget import RepoWidget

from core.communication_manager import CommunicationManager
from core.session.workspace import Workspace
from core.processing.performance import PerformanceMonitor

APP_TITLE = "Gemini OBD-II Diagnostic Tool"
APP_VERSION = "2.2 (Repo Enabled)"

class MainWindow(QMainWindow):
    # Signals to communicate with worker thread
    sig_connect = pyqtSignal(dict)
    sig_disconnect = pyqtSignal()
    sig_execute = pyqtSignal(str, object) # cmd_name, cmd_obj/str

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_TITLE} v{APP_VERSION}")
        self.setGeometry(100, 100, 1200, 700)
        self.set_icon()

        self.workspace = Workspace()
        self.current_workspace_path = None
        self.perf_monitor = PerformanceMonitor()

        self.init_ui()
        self.create_menu_bar()
        self.init_communication()
        self.apply_stylesheet()

    def init_ui(self):
        # --- Create Widgets ---
        self.connection_widget = ConnectionWidget()
        self.command_widget = CommandWidget()
        self.data_view_widget = DataViewWidget()
        self.log_widget = LogWidget()
        self.dashboard_widget = DashboardWidget()
        self.repo_widget = RepoWidget()

        # Phase 5: Analysis
        from core.processing.analysis import TrafficMonitor
        # Ideally monitor is shared with CommManager, for now instantiate locally
        # or better: CommManager emits signals that Main connects to Monitor.
        self.traffic_monitor = TrafficMonitor(self.repo_widget.db_manager) 
        # Inject DBManager for decoding
        
        from gui.widgets.analysis_widget import AnalysisWidget
        self.analysis_widget = AnalysisWidget(self.traffic_monitor)
        
        # Phase 7: Discovery Wizard
        from gui.widgets.discovery_widget import DiscoveryWidget
        self.discovery_widget = DiscoveryWidget(self.traffic_monitor)
        
        # Phase 8: Architecture Widget
        from gui.widgets.architecture_widget import ArchitectureWidget
        # We need to pass the connection manager (or traffic monitor if that's what we use)
        # Note: ActiveScanner takes connection_manager, but for now we might mock or pass None if unconnected
        # Actually ConnectionWidget holds the logic. We should probably pass the whole connection widget or extract the manager.
        # For this prototype, we'll pass the connection_widget which acts as manager proxy.
        self.arch_widget = ArchitectureWidget(self.connection_widget)
        
        # Phase 13: SWDL Widget
        from gui.widgets.swdl_widget import SWDLWidget
        self.swdl_widget = SWDLWidget(self.connection_widget)
        
        # Phase 14: Service Widget
        from gui.widgets.service_widget import ServiceWidget
        self.service_widget = ServiceWidget(self.connection_widget)
        
        # from core.processing.mock_traffic import MockTrafficGenerator
        # self.mock_gen = MockTrafficGenerator(self.traffic_monitor)
        # self.mock_gen.start() # Auto-start for demo
        
        self.data_view_widget.populate_initial_data(DEFAULT_COMMANDS_J1979.keys())

        # --- Layout ---
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        left_column = self.connection_widget
        
        # Center column: Tabs for Command/Data vs Dashboard
        self.tabs = QTabWidget()
        
        # Tab 1: Diagnostics
        diag_widget = QWidget()
        diag_layout = QHBoxLayout(diag_widget)
        diag_layout.addWidget(self.command_widget)
        
        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        right_layout.addWidget(self.data_view_widget, 1)
        right_layout.addWidget(self.log_widget, 1)
        diag_layout.addWidget(right_column, 1)
        
        # Add Tabs
        self.tabs.addTab(diag_widget, "Diagnostics")
        self.tabs.addTab(self.arch_widget, "Architecture") # Phase 8
        self.tabs.addTab(self.dashboard_widget, "Dashboard")
        self.tabs.addTab(self.repo_widget, "Repository")
        self.tabs.addTab(self.analysis_widget, "Competitor Analysis")
        self.tabs.addTab(self.swdl_widget, "Software Download")
        self.tabs.addTab(self.service_widget, "Service Functions")
        # Remapping functionality removed as per user request
        self.tabs.addTab(self.discovery_widget, "Wizard")
        
        main_layout.addWidget(left_column)
        main_layout.addWidget(self.tabs, 1)

        # --- Manual Signals ---
        self.connection_widget.connect_clicked.connect(self.start_connection)
        self.connection_widget.disconnect_clicked.connect(self.stop_connection)
        self.command_widget.command_triggered.connect(self.on_command_triggered)

    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu('&File')
        
        new_ws_action = QAction('&New Workspace', self)
        new_ws_action.triggered.connect(self.new_workspace)
        file_menu.addAction(new_ws_action)

        open_ws_action = QAction('&Open Workspace', self)
        open_ws_action.triggered.connect(self.open_workspace)
        file_menu.addAction(open_ws_action)

        save_ws_action = QAction('&Save Workspace', self)
        save_ws_action.triggered.connect(self.save_workspace)
        file_menu.addAction(save_ws_action)
        
        file_menu.addSeparator()
        exit_action = QAction('&Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def init_communication(self):
        self.comm_thread = QThread()
        self.comm_worker = CommunicationManager()
        self.comm_worker.moveToThread(self.comm_thread)

        # Connect Worker signals to GUI
        self.comm_worker.connection_status.connect(self.on_connection_status)
        self.comm_worker.log_message.connect(self.log_widget.add_log)
        self.comm_worker.data_received.connect(self.on_data_received)
        
        # Connect GUI signals to Worker slots
        self.sig_connect.connect(self.comm_worker.connect_vehicle)
        self.sig_disconnect.connect(self.comm_worker.disconnect_vehicle)
        self.sig_execute.connect(self.comm_worker.execute_command)

        self.comm_thread.start()

    def on_data_received(self, name, value):
        # Update Data Grid
        self.data_view_widget.update_data(name, value)
        # Update Dashboard
        self.dashboard_widget.update_data(name, value)
        
        # Update Performance Monitor
        if "Speed" in name:
            try:
                # Basic parsing "12.0 mph" -> 12.0
                val = float(value.split(' ')[0])
                self.perf_monitor.update_speed(val)
                self.dashboard_widget.update_perf_status(self.perf_monitor.get_status())
            except:
                pass

    def start_connection(self, config):
        # We transform the widget config to our internal config format if needed
        # basic mapping
        internal_config = {}
        if config['type'] == 'ELM327 (Serial)':
            internal_config = {"adapter_type": "ELM327", "port": config['port']}
        elif config['type'] == 'DoIP (Ethernet)':
            internal_config = {"adapter_type": "DoIP", "ip": config['ip'], "address": config['address']}
        else:
            self.log_widget.add_log(f"ERROR: Unknown adapter type '{config['type']}'")
            return

        self.log_widget.add_log(f"INFO: Connecting to {internal_config['adapter_type']}...")
        self.connection_widget.set_status(False, "Connecting...")
        
        # Signal to worker
        self.sig_connect.emit(internal_config)

    def stop_connection(self):
        self.sig_disconnect.emit()

    def on_connection_status(self, is_connected, message):
        self.connection_widget.set_status(is_connected, message)

    def on_command_triggered(self, name, command_obj, command_hex):
        # We need to decide what to pass based on adapter type, 
        # but CommunicationManager handles the adapter now.
        # We pass both obj (for ELM) and hex (for DoIP) or let Manager handle it?
        # Current execute_command signature is (cmd_name, cmd)
        # We will pass the command object for ELM, and maybe hex for others.
        # Ideally, command_widget should give us a unified command structure.
        # For now, we pass what we have.
        cmd = command_obj if command_obj else command_hex
        self.sig_execute.emit(name, cmd)

    # --- Workspace Handlers ---
    def new_workspace(self):
        self.workspace = Workspace()
        self.current_workspace_path = None
        self.log_widget.add_log("INFO: New Workspace created.")

    def open_workspace(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open Workspace', '', "Workspace Files (*.ws)")
        if fname:
            try:
                self.workspace.load(fname)
                self.current_workspace_path = fname
                self.log_widget.add_log(f"INFO: Loaded workspace: {self.workspace.name}")
                # Restore settings/state here if valid
            except Exception as e:
                self.log_widget.add_log(f"ERROR: Failed to load workspace: {e}")

    def save_workspace(self):
        if not self.current_workspace_path:
             fname, _ = QFileDialog.getSaveFileName(self, 'Save Workspace', '', "Workspace Files (*.ws)")
             if fname:
                 self.current_workspace_path = fname
        
        if self.current_workspace_path:
            try:
                self.workspace.name = os.path.basename(self.current_workspace_path)
                self.workspace.save(self.current_workspace_path)
                self.log_widget.add_log(f"INFO: Saved workspace to {self.current_workspace_path}")
            except Exception as e:
                self.log_widget.add_log(f"ERROR: Failed to save workspace: {e}")

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
        self.stop_connection()
        self.comm_thread.quit()
        self.comm_thread.wait(1000)
        event.accept()
