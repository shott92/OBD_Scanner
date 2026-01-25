# gui/widgets/command_widget.py
import obd
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QDialog, QLineEdit, QFormLayout, QHBoxLayout
from PyQt5.QtCore import pyqtSignal

DEFAULT_COMMANDS_J1979 = {
    "Read RPM": (obd.commands.RPM, "010C"),
    "Read Vehicle Speed": (obd.commands.SPEED, "010D"),
    "Read Coolant Temp": (obd.commands.COOLANT_TEMP, "0105"),
    "Get DTCs": (obd.commands.GET_DTC, "03"),
}

DEFAULT_COMMANDS_UDS = {
    "Session Control (Diagnostic)": "1003",
    "Session Control (Programming)": "1002",
    "ECU Reset (Hard)": "1101",
    "ECU Reset (KeyOffOn)": "1102",
    "Read VIN (DID F190)": "22F190",
    "Read HW PN (DID F191)": "22F191",
    "Tester Present": "3E80",
}

class CommandWidget(QGroupBox):
    """Widget for holding and managing command buttons."""
    # Signal emits: command_name, obd.Command object, command_hex_payload
    command_triggered = pyqtSignal(str, object, str)

    def __init__(self, title="Vehicle Commands"):
        super().__init__(title)
        self.main_layout = QVBoxLayout()
        
        # J1979 Section
        j1979_group = QGroupBox("SAE J1979 Standard PIDs")
        j1979_layout = QVBoxLayout()
        for name, (cmd_obj, cmd_hex) in DEFAULT_COMMANDS_J1979.items():
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, n=name, c_obj=cmd_obj, c_hex=cmd_hex: self.command_triggered.emit(n, c_obj, c_hex))
            j1979_layout.addWidget(btn)
        j1979_group.setLayout(j1979_layout)
        
        # UDS / Custom Section
        self.uds_group = QGroupBox("ISO 14229 UDS / Custom")
        self.uds_layout = QVBoxLayout()
        
        # Pre-populate UDS
        for name, cmd_hex in DEFAULT_COMMANDS_UDS.items():
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, n=name, c_hex=cmd_hex: self.command_triggered.emit(n, None, c_hex))
            self.uds_layout.addWidget(btn)
        
        add_cmd_button = QPushButton("+ Add New Command")
        add_cmd_button.clicked.connect(self.show_add_command_dialog)
        self.uds_layout.addWidget(add_cmd_button)
        self.uds_group.setLayout(self.uds_layout)

        self.main_layout.addWidget(j1979_group)
        self.main_layout.addWidget(self.uds_group)
        self.main_layout.addStretch()
        self.setLayout(self.main_layout)

    def show_add_command_dialog(self):
        # Implementation for adding custom UDS commands
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Custom UDS Command")
        form_layout = QFormLayout(dialog)

        name_edit = QLineEdit(dialog)
        cmd_edit = QLineEdit(dialog)
        
        form_layout.addRow("Command Name:", name_edit)
        form_layout.addRow("UDS Hex Payload (e.g., 22F190):", cmd_edit)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(lambda: self.add_custom_command(name_edit.text(), cmd_edit.text(), dialog))
        
        form_layout.addWidget(ok_button)
        dialog.exec_()
        
    def add_custom_command(self, name, command_hex, dialog):
        if not name or not command_hex: return
        try:
            bytes.fromhex(command_hex) # Validate hex
        except ValueError: return

        btn = QPushButton(name)
        # For custom commands, the obd.Command object is None
        btn.clicked.connect(lambda _, n=name, c_hex=command_hex: self.command_triggered.emit(n, None, c_hex))
        self.uds_layout.addWidget(btn)
        dialog.accept()
