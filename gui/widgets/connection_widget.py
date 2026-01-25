from PyQt5.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QStackedWidget, QWidget,
                             QFormLayout, QLineEdit, QCheckBox)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSignal
import serial.tools.list_ports

class ConnectionWidget(QGroupBox):
    """Widget for managing adapter connection settings."""
    connect_clicked = pyqtSignal(dict)
    disconnect_clicked = pyqtSignal()

    def __init__(self, title="Connection Manager"):
        super().__init__(title)
        self.setFixedWidth(300)
        
        # Main layout
        layout = QVBoxLayout()

        # --- Adapter Type Selection ---
        adapter_type_layout = QHBoxLayout()
        adapter_type_layout.addWidget(QLabel("Adapter Type:"))
        self.adapter_type_combo = QComboBox()
        self.adapter_type_combo.addItems(["ELM327 (Serial)", "DoIP (Ethernet)"])
        adapter_type_layout.addWidget(self.adapter_type_combo)
        
        # --- Stacked Widget for Settings ---
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self._create_elm327_ui())
        self.stacked_widget.addWidget(self._create_doip_ui())
        
        self.adapter_type_combo.currentIndexChanged.connect(self.stacked_widget.setCurrentIndex)
        
        # --- Advanced Settings ---
        self.tester_present_cb = QCheckBox("Enable Tester Present (Keep-Alive)")
        self.tester_present_cb.setToolTip("Sends $3E 80 every 2 seconds")

        # --- Connection Buttons and Status ---
        self.connect_button = QPushButton("Connect")
        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.setEnabled(False)
        
        self.status_light = QLabel()
        self.status_light.setObjectName("status_light") # For CSS
        self.status_label = QLabel("Status: Disconnected")
        
        status_layout = QHBoxLayout()
        status_layout.addWidget(self.status_light)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        # --- Button connections ---
        self.connect_button.clicked.connect(self._on_connect_click)
        self.disconnect_button.clicked.connect(self.disconnect_clicked.emit)
        
        # --- Advanced Button ---
        self.advanced_btn = QPushButton("Advanced Config")
        self.advanced_btn.clicked.connect(self.open_advanced_config)
        self.advanced_settings = {} # Store advanced config here

        # --- Add all widgets to layout ---
        layout.addLayout(adapter_type_layout)
        layout.addWidget(self.stacked_widget)
        layout.addWidget(self.tester_present_cb)
        
        btns_layout = QHBoxLayout()
        btns_layout.addWidget(self.connect_button)
        btns_layout.addWidget(self.advanced_btn)
        
        layout.addLayout(btns_layout)
        layout.addWidget(self.disconnect_button)
        layout.addLayout(status_layout)
        
        self.setLayout(layout)
        self.set_status(False, "Disconnected")

    def _create_elm327_ui(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)
        
        self.port_combo = QComboBox()
        self.refresh_ports()
        
        layout.addRow("Serial Port:", self.port_combo)
        return widget
        
    def _create_doip_ui(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)
        
        self.ip_edit = QLineEdit("127.0.0.1") 
        self.addr_edit = QLineEdit("0x0E00")   # Logical Addr (Diag Client)
        self.target_edit = QLineEdit("0x1000") # Target ECU Addr
        
        layout.addRow("Gateway IP:", self.ip_edit)
        layout.addRow("My Logical Address:", self.addr_edit)
        layout.addRow("Target Address:", self.target_edit)
        return widget

    def refresh_ports(self):
        self.port_combo.clear()
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo.addItems(ports if ports else ["No ports found"])

    def open_advanced_config(self):
        from gui.dialogs.advanced_network_dialog import AdvancedNetworkDialog
        dlg = AdvancedNetworkDialog(self.advanced_settings, self)
        if dlg.exec_():
            self.advanced_settings = dlg.get_settings()
            # print("Advanced Debug:", self.advanced_settings) # Debug

    def _on_connect_click(self):
        config = {
            'type': self.adapter_type_combo.currentText(),
            'tester_present': self.tester_present_cb.isChecked()
        }
        if config['type'] == 'ELM327 (Serial)':
            config['port'] = self.port_combo.currentText()
        else:
            config['ip'] = self.ip_edit.text()
            config['address'] = self.addr_edit.text()
            config['target_address'] = self.target_edit.text()
        
        # Merge advanced settings
        config.update(self.advanced_settings)
        
        self.connect_clicked.emit(config)

    def set_status(self, is_connected, message):
        color = QColor("lime") if is_connected else QColor("red")
        self.status_light.setFixedSize(16, 16)
        self.status_light.setStyleSheet(f"background-color: {color.name()};")
        self.status_label.setText(f"Status: {message}")
        
        self.connect_button.setEnabled(not is_connected)
        self.disconnect_button.setEnabled(is_connected)
        self.adapter_type_combo.setEnabled(not is_connected)
