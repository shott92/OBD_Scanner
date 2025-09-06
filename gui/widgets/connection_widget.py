# gui/widgets/connection_widget.py
import json
import os
from PyQt5.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QStackedWidget, QWidget,
                             QFormLayout, QLineEdit)
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

        # --- Add all widgets to layout ---
        layout.addLayout(adapter_type_layout)
        layout.addWidget(self.stacked_widget)
        layout.addWidget(self.connect_button)
        layout.addWidget(self.disconnect_button)
        layout.addLayout(status_layout)

        self.setLayout(layout)
        self.set_status(False, "Disconnected")

        self._load_ecus()

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

        self.ecu_combo = QComboBox()
        self.ecu_combo.currentIndexChanged.connect(self._on_ecu_selected)

        self.ip_edit = QLineEdit("127.0.0.1") # Default for simulators
        self.addr_edit = QLineEdit("0xFE")   # Common logical address

        layout.addRow("Target ECU:", self.ecu_combo)
        layout.addRow("Vehicle IP:", self.ip_edit)
        layout.addRow("ECU Address (Hex):", self.addr_edit)
        return widget

    def _load_ecus(self):
        self.ecu_list = []
        try:
            path = os.path.join(os.path.dirname(__file__), '..', '..', 'ecus.json')
            with open(path, 'r') as f:
                self.ecu_list = json.load(f)

            self.ecu_combo.addItem("Custom")
            for ecu in self.ecu_list:
                self.ecu_combo.addItem(ecu.get("name", "Unknown ECU"))

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"WARN: Could not load ecus.json: {e}")
            self.ecu_combo.addItem("No ECUs loaded")
            self.ecu_combo.setEnabled(False)

    def _on_ecu_selected(self, index):
        # Index 0 is "Custom"
        if index > 0 and self.ecu_list:
            selected_ecu = self.ecu_list[index - 1]
            self.addr_edit.setText(selected_ecu.get("address", ""))
            self.addr_edit.setReadOnly(True)
        else:
            self.addr_edit.setReadOnly(False)


    def refresh_ports(self):
        self.port_combo.clear()
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo.addItems(ports if ports else ["No ports found"])

    def _on_connect_click(self):
        config = {'type': self.adapter_type_combo.currentText()}
        if config['type'] == 'ELM327 (Serial)':
            config['port'] = self.port_combo.currentText()
        else:
            config['ip'] = self.ip_edit.text()
            config['address'] = self.addr_edit.text()
        self.connect_clicked.emit(config)

    def set_status(self, is_connected, message):
        color = QColor("lime") if is_connected else QColor("red")
        self.status_light.setFixedSize(16, 16)
        self.status_light.setStyleSheet(f"background-color: {color.name()};")
        self.status_label.setText(f"Status: {message}")

        self.connect_button.setEnabled(not is_connected)
        self.disconnect_button.setEnabled(is_connected)
        self.adapter_type_combo.setEnabled(not is_connected)
        if hasattr(self, 'ecu_combo') and self.ecu_combo.isEnabled():
            self.ecu_combo.setEnabled(not is_connected)
