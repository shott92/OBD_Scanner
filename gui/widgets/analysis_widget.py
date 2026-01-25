from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLabel, QSplitter, QTextEdit)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor

class AnalysisWidget(QWidget):
    def __init__(self, traffic_monitor):
        super().__init__()
        self.monitor = traffic_monitor
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_view)
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        splitter = QSplitter(Qt.Vertical)
        
        # --- Top: Traffic Table (Heatmap-ish) ---
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID (Hex)", "Count", "Freq (Hz)", "Interval (ms)", "Known?", "Data (Hex)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.itemClicked.connect(self.on_row_clicked)
        
        splitter.addWidget(self.table)
        
        # --- Bottom: Detail / Decoder View ---
        self.details = QTextEdit()
        self.details.setReadOnly(True)
        self.details.setPlaceholderText("Select a message to view decoded signals...")
        splitter.addWidget(self.details)
        
        layout.addWidget(splitter)
        
        self.timer.start(500) # Update every 500ms

    def update_view(self):
        snapshot = self.monitor.get_snapshot()
        
        # Update table rows. 
        # Note: Re-creating rows every 500ms is inefficient for 1000s of IDs, 
        # but fine for V1 (<100 IDs usually active).
        
        # We'll map existing rows to IDs to avoid full redraw
        existing_ids = {}
        for row in range(self.table.rowCount()):
             item = self.table.item(row, 0)
             if item:
                 existing_ids[int(item.text(), 16)] = row
        
        active_ids = sorted(snapshot.keys())
        
        # Add new rows
        for aid in active_ids:
            if aid not in existing_ids:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(f"{aid:03X}"))
                self.table.setItem(row, 1, QTableWidgetItem("0")) # Count
                self.table.setItem(row, 2, QTableWidgetItem("0.0")) # Freq
                self.table.setItem(row, 3, QTableWidgetItem("0")) # Interval
                self.table.setItem(row, 4, QTableWidgetItem("No")) # Known
                self.table.setItem(row, 5, QTableWidgetItem("")) # Data
                existing_ids[aid] = row
        
        # Update data
        for aid, data in snapshot.items():
            row = existing_ids[aid]
            
            # Count
            self.table.item(row, 1).setText(str(data['count']))
            
            # Freq
            freq = 1.0 / data['avg_interval'] if data['avg_interval'] > 0 else 0.0
            self.table.item(row, 2).setText(f"{freq:.1f}")
            
            # Interval
            ms = data['avg_interval'] * 1000
            self.table.item(row, 3).setText(f"{ms:.1f}")
            
            # Known/Color
            known_item = self.table.item(row, 4)
            known_item.setText("YES" if data['is_known'] else "No")
            if data['is_known']:
                known_item.setBackground(QColor(200, 255, 200)) # Light Green
            else:
                known_item.setBackground(QColor(255, 220, 220)) # Light Red
            
            # Data
            hex_data = data['data'].hex().upper()
            self.table.item(row, 5).setText(hex_data)

    def on_row_clicked(self, item):
        row = item.row()
        id_item = self.table.item(row, 0)
        if not id_item: return
        
        arb_id = int(id_item.text(), 16)
        entry = self.monitor.messages.get(arb_id)
        
        if entry:
            txt = f"ID: 0x{arb_id:X}\n"
            txt += f"Count: {entry['count']}\n"
            txt += f"Data: {entry['data'].hex().upper()}\n"
            txt += "-"*20 + "\n"
            if entry['is_known'] and entry['decoded']:
                txt += "DECODED SIGNALS:\n"
                for sig, val in entry['decoded'].items():
                    txt += f"{sig}: {val}\n"
            else:
                txt += "No decoding available (Unknown ID)."
            
            self.details.setText(txt)
