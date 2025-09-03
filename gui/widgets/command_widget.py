# gui/widgets/command_widget.py
import obd
import json
import os
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QDialog, QLineEdit, QFormLayout
from PyQt5.QtCore import pyqtSignal

class CommandWidget(QGroupBox):
    """Widget for holding and managing command buttons."""
    # Signal emits: command_name, obd.Command object, command_hex_payload
    command_triggered = pyqtSignal(str, object, str)

    def __init__(self, title="Vehicle Commands"):
        super().__init__(title)
        self.main_layout = QVBoxLayout()

        self.j1979_group = QGroupBox("SAE J1979 Standard PIDs")
        self.j1979_layout = QVBoxLayout()
        self.j1979_group.setLayout(self.j1979_layout)

        self.uds_group = QGroupBox("ISO 14229 UDS / Custom")
        self.uds_layout = QVBoxLayout()
        add_cmd_button = QPushButton("+ Add New Command")
        add_cmd_button.clicked.connect(self.show_add_command_dialog)
        self.uds_layout.addWidget(add_cmd_button)
        self.uds_group.setLayout(self.uds_layout)

        self.main_layout.addWidget(self.j1979_group)
        self.main_layout.addWidget(self.uds_group)
        self.main_layout.addStretch()
        self.setLayout(self.main_layout)

        self.load_commands()

    def load_commands(self):
        """Loads commands from the commands.json file."""
        try:
            # Assumes commands.json is in the root directory
            path = os.path.join(os.path.dirname(__file__), '..', '..', 'commands.json')
            with open(path, 'r') as f:
                commands = json.load(f)

            # Populate J1979 commands
            for cmd_def in commands.get("J1979", []):
                name = cmd_def.get("name")
                obd_cmd_name = cmd_def.get("obd_command")
                cmd_hex = cmd_def.get("hex")

                if not all([name, obd_cmd_name, cmd_hex]):
                    print(f"WARN: Skipping invalid J1979 command definition: {cmd_def}")
                    continue

                try:
                    # Look up the command object from python-obd library
                    cmd_obj = obd.commands[obd_cmd_name]
                    btn = QPushButton(name)
                    btn.clicked.connect(lambda _, n=name, c_obj=cmd_obj, c_hex=cmd_hex: self.command_triggered.emit(n, c_obj, c_hex))
                    self.j1979_layout.addWidget(btn)
                except KeyError:
                    print(f"WARN: OBD command '{obd_cmd_name}' not found in python-obd library.")

            # Populate UDS commands (if any are predefined)
            for cmd_def in commands.get("UDS", []):
                name = cmd_def.get("name")
                cmd_hex = cmd_def.get("hex")
                if name and cmd_hex:
                     self.add_custom_command(name, cmd_hex)

        except FileNotFoundError:
            print("ERROR: commands.json not found. No default commands will be loaded.")
        except json.JSONDecodeError:
            print("ERROR: Could not decode commands.json. Check for syntax errors.")

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
        ok_button.clicked.connect(lambda: self.add_custom_command_from_dialog(name_edit.text(), cmd_edit.text(), dialog))

        form_layout.addWidget(ok_button)
        dialog.exec_()

    def add_custom_command_from_dialog(self, name, command_hex, dialog):
        """Adds a command from the dialog and closes it."""
        if self.add_custom_command(name, command_hex):
            dialog.accept()

    def add_custom_command(self, name, command_hex):
        """Adds a custom command button to the UDS group."""
        if not name or not command_hex:
            return False
        try:
            bytes.fromhex(command_hex) # Validate hex
        except ValueError:
            # Optionally show an error to the user
            return False

        btn = QPushButton(name)
        # For custom commands, the obd.Command object is None
        btn.clicked.connect(lambda _, n=name, c_hex=command_hex: self.command_triggered.emit(n, None, c_hex))

        # Insert new command before the "+ Add New Command" button
        self.uds_layout.insertWidget(self.uds_layout.count() - 1, btn)
        return True
