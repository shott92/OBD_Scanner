# gui/widgets/data_view_widget.py
from PyQt5.QtWidgets import QTableView, QAbstractItemView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt

class DataViewWidget(QTableView):
    """
    A widget to display key-value data in a table.
    """
    def __init__(self):
        super().__init__()
        self.model = QStandardItemModel(0, 2) # 0 rows, 2 columns
        self.model.setHorizontalHeaderLabels(['Parameter', 'Value'])
        self.setModel(self.model)

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)

        self.data_items = {} # To keep track of items by name

    def populate_initial_data(self, data_keys):
        """
        Populates the table with initial keys and default values.
        """
        for key in data_keys:
            if key not in self.data_items:
                param_item = QStandardItem(key)
                value_item = QStandardItem("N/A")
                self.model.appendRow([param_item, value_item])
                self.data_items[key] = value_item

    def update_data(self, key, value):
        """
        Updates the value for a given key in the table.
        If the key doesn't exist, it adds a new row.
        """
        if key in self.data_items:
            self.data_items[key].setText(str(value))
        else:
            # If a command is not in the initial list (e.g., custom UDS)
            param_item = QStandardItem(key)
            value_item = QStandardItem(str(value))
            self.model.appendRow([param_item, value_item])
            self.data_items[key] = value_item
