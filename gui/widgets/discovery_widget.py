from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QComboBox, QTableWidget, QTableWidgetItem, 
                             QProgressBar, QHeaderView, QMessageBox, QGroupBox)
from PyQt5.QtCore import QTimer, Qt
from core.processing.correlator import Correlator
from collections import defaultdict

class DiscoveryWidget(QWidget):
    def __init__(self, traffic_monitor):
        super().__init__()
        self.monitor = traffic_monitor
        self.correlator = Correlator()
        
        self.recording = False
        self.log_data = [] # List of (ts, id, data)
        
        self.init_ui()
        
        # Timer for polling
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self.poll_traffic)
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        self.lbl_instruct = QLabel("1. select Action. 2. Press Record. 3. Follow prompts.")
        self.lbl_instruct.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.lbl_instruct)
        
        # Controls
        ctrl_layout = QHBoxLayout()
        self.combo_action = QComboBox()
        self.combo_action.addItems([
            "Brake Pedal (Sweep)", "Throttle Pedal (Sweep)", "Clutch (Sweep)",
            "Left Indicator", "Right Indicator", 
            "Headlights", "Window Up", "Window Down"
        ])
        
        self.btn_record = QPushButton("Record")
        self.btn_record.clicked.connect(self.toggle_record)
        
        self.btn_reset = QPushButton("Reset")
        self.btn_reset.clicked.connect(self.reset_wizard)
        
        ctrl_layout.addWidget(self.combo_action, 1)
        ctrl_layout.addWidget(self.btn_record)
        ctrl_layout.addWidget(self.btn_reset)
        layout.addLayout(ctrl_layout)
        
        self.lbl_status = QLabel("Ready.")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setStyleSheet("color: gray; font-size: 16px;")
        layout.addWidget(self.lbl_status)
        
        # Results Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Candidate", "ID (Hex)", "Byte", "Bit", "Type"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        # Save Panel
        self.grp_save = QGroupBox("Save Candidate")
        save_layout = QHBoxLayout()
        self.lbl_candidate = QLabel("Select a row to save.")
        self.btn_save_dbc = QPushButton("Add to local DBC")
        self.btn_save_dbc.setEnabled(False)
        self.btn_save_dbc.clicked.connect(self.save_to_dbc)
        
        save_layout.addWidget(self.lbl_candidate)
        save_layout.addWidget(self.btn_save_dbc)
        self.grp_save.setLayout(save_layout)
        layout.addWidget(self.grp_save)

    def toggle_record(self):
        if not self.recording:
            # Start Recording
            self.recording = True
            self.log_data = [] # Clear log
            self.btn_record.setText("Stop")
            self.btn_reset.setEnabled(False)
            self.poll_timer.start(10) # 100Hz polling (fast!)
            
            # Guide the user
            self.lbl_status.setText("Recording Baseline... STAY IDLE (1s)")
            self.lbl_status.setStyleSheet("color: orange; font-weight: bold;")
            
            # Schedule text update
            QTimer.singleShot(1500, lambda: self.update_prompt_action())
            
        else:
            # Stop Recording
            self.recording = False
            self.btn_record.setText("Record")
            self.btn_reset.setEnabled(True)
            self.poll_timer.stop()
            self.lbl_status.setText("Analyzing...")
            self.lbl_status.setStyleSheet("color: blue;")
            self.run_analysis()

    def update_prompt_action(self):
        if self.recording:
            self.lbl_status.setText("GO! Perform Action NOW!")
            self.lbl_status.setStyleSheet("color: green; font-weight: bold; font-size: 18px;")

    def poll_traffic(self):
        # Poll monitor for NEW frames. 
        # Since monitor aggregates, we have to cheat slightly for V1 and just grab LATEST snapshot.
        # Ideally monitor emits signal 'frame_received(id, data, ts)'
        # We will iterate monitor.messages and grab 'last_ts' > last_poll_time?
        # Simpler: Just rely on monitor's state.
        
        import time
        now = time.time()
        
        # In a real app we'd consume a queue. Here we scan.
        # To avoid duplicates, we'd need tracking.
        # For this prototype: Assume we catch *most* frames by high polling rate.
        # But for 'change detection', misses are okay if we catch the state transition.
        
        snapshot = self.monitor.messages
        for aid, entry in snapshot.items():
            # If updated recently (within last 20ms)
             if entry['last_ts'] > (now - 0.02):
                 self.log_data.append((entry['last_ts'], aid, entry['data']))

    def run_analysis(self):
        candidates = self.correlator.analyze_series(self.log_data)
        
        self.table.setRowCount(0)
        for i, c in enumerate(candidates):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(c['desc']))
            self.table.setItem(i, 1, QTableWidgetItem(f"{c['id']:X}"))
            self.table.setItem(i, 2, QTableWidgetItem(str(c['byte'])))
            self.table.setItem(i, 3, QTableWidgetItem(str(c['bit'])))
            self.table.setItem(i, 4, QTableWidgetItem(c['change']))
            
        if not candidates:
            # QMessageBox.information(self, "Result", "No strong correlation found.")
            self.lbl_status.setText("No correlation found. Try again.")
            self.lbl_status.setStyleSheet("color: red;")
        else:
            self.lbl_status.setText(f"Found {len(candidates)} candidates.")
            self.lbl_status.setStyleSheet("color: black;")

    def reset_wizard(self):
        self.log_data = []
        self.table.setRowCount(0)
        self.lbl_status.setText("Ready.")
        self.lbl_status.setStyleSheet("color: gray;")

    def save_to_dbc(self):
        QMessageBox.information(self, "Features", "DBC Writing coming in next update!")
