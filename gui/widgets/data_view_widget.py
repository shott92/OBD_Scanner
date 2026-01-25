from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt

class DataViewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.items = {}

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Parameter", "Value", "Unit"])
        layout.addWidget(self.tree)

    def populate_initial_data(self, command_names):
        self.tree.clear()
        self.items = {}
        for name in command_names:
            item = QTreeWidgetItem([name, "N/A", ""])
            self.tree.addTopLevelItem(item)
            self.items[name] = item

    def update_data(self, cmd_name, value):
        if cmd_name in self.items:
            # Simple parsing if value contains unit (e.g. "12.5 V")
            # This is a basic implementation
            parts = value.split(' ', 1)
            val = parts[0]
            unit = parts[1] if len(parts) > 1 else ""
            
            self.items[cmd_name].setText(1, val)
            self.items[cmd_name].setText(2, unit)
        else:
            # Add dynamic item if not known suitable for discovery
            item = QTreeWidgetItem([cmd_name, value, ""])
            self.tree.addTopLevelItem(item)
            self.items[cmd_name] = item
