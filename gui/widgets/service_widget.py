from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QGroupBox, QComboBox, QTreeWidget, QTreeWidgetItem, QMessageBox, QHeaderView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from core.diagnostics.service_manager import ServiceManager

class ServiceWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args
        
    def run(self):
        try:
            self.func(*self.args, progress_callback=self.report_progress)
            self.finished.emit(True, "Operation Successful")
        except Exception as e:
            self.finished.emit(False, str(e))
            
    def report_progress(self, val, text):
        self.progress.emit(val, text)

class ServiceWidget(QWidget):
    def __init__(self, connection_manager=None):
        super().__init__()
        self.conn = connection_manager
        self.manager = ServiceManager(connection_manager)
        self.worker = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Service Functions & Variant Coding")
        header.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header)
        
        # ECU Selector
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Target ECU:"))
        self.combo_ecu = QComboBox()
        self.combo_ecu.addItems(["BCM", "PCM", "IPC", "ABS"]) # Hardcoded shortlist for now
        self.combo_ecu.currentTextChanged.connect(self.load_functions)
        hbox.addWidget(self.combo_ecu)
        hbox.addStretch()
        layout.addLayout(hbox)
        
        # Function Tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Function Name", "Type / ID", "Value / State"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tree.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.tree)
        
        # Execution Controls
        grp_exec = QGroupBox("Control Panel")
        vbox = QVBoxLayout()
        self.lbl_selected = QLabel("Select a function...")
        self.lbl_selected.setStyleSheet("font-weight: bold;")
        
        self.btn_run = QPushButton("Execute Function")
        self.btn_run.clicked.connect(self.execute_function)
        self.btn_run.setEnabled(False)
        self.btn_run.setStyleSheet("background-color: #e6f3ff;")
        
        self.lbl_status = QLabel("Ready")
        
        vbox.addWidget(self.lbl_selected)
        vbox.addWidget(self.btn_run)
        vbox.addWidget(self.lbl_status)
        grp_exec.setLayout(vbox)
        layout.addWidget(grp_exec)
        
        # Initial Load
        self.load_functions(self.combo_ecu.currentText())

    def load_functions(self, ecu_name):
        self.tree.clear()
        defs = self.manager.load_definitions(ecu_name)
        
        # 1. Routines
        root_routines = QTreeWidgetItem(self.tree)
        root_routines.setText(0, "Service Procedures (0x31)")
        root_routines.setExpanded(True)
        
        for r in defs.get('routines', []):
            item = QTreeWidgetItem(root_routines)
            item.setText(0, r['name'])
            item.setText(1, f"0x{r['id']:04X}")
            item.setToolTip(0, r.get('description', ''))
            item.setData(0, Qt.UserRole, {'type': 'routine', 'data': r})
            
        # 2. IO Control
        root_io = QTreeWidgetItem(self.tree)
        root_io.setText(0, "Output Control (0x2F)")
        root_io.setExpanded(True)
        
        for io in defs.get('io_controls', []):
            item = QTreeWidgetItem(root_io)
            item.setText(0, io['name'])
            item.setText(1, f"0x{io['id']:04X}")
            item.setData(0, Qt.UserRole, {'type': 'io', 'data': io})
            
        # 3. Coding
        root_coding = QTreeWidgetItem(self.tree)
        root_coding.setText(0, "Configuration (0x2E)")
        root_coding.setExpanded(True)
        
        for c in defs.get('coding', []):
            item = QTreeWidgetItem(root_coding)
            item.setText(0, c['name'])
            item.setText(1, f"0x{c['id']:X}")
            item.setText(2, str(c['value']))
            item.setData(0, Qt.UserRole, {'type': 'coding', 'data': c})

    def on_item_clicked(self, item, col):
        data = item.data(0, Qt.UserRole)
        if not data:
            self.lbl_selected.setText("Select a function...")
            self.btn_run.setEnabled(False)
            return
            
        obj = data['data']
        self.lbl_selected.setText(f"{obj['name']}")
        
        if data['type'] == 'routine':
            self.btn_run.setText("Run Routine")
        elif data['type'] == 'io':
            self.btn_run.setText("Toggle State") # Simplified
        elif data['type'] == 'coding':
            self.btn_run.setText("Write Coding")
            
        self.btn_run.setEnabled(True)

    def execute_function(self):
        item = self.tree.currentItem()
        if not item: return
        data = item.data(0, Qt.UserRole)
        obj = data['data']
        type_ = data['type']
        
        if type_ == 'routine':
            # Run Routine
            self.btn_run.setEnabled(False)
            self.worker = ServiceWorker(self.manager.execute_routine, 0x00, obj['id'])
            self.worker.progress.connect(self.update_status)
            self.worker.finished.connect(self.on_finished)
            self.worker.start()
            
        elif type_ == 'io':
            # Toggle (Mock)
            self.btn_run.setEnabled(False)
            self.worker = ServiceWorker(self.manager.execute_io_control, 0x00, obj['id'], "TOGGLE")
            self.worker.progress.connect(self.update_status)
            self.worker.finished.connect(self.on_finished)
            self.worker.start()
            
        elif type_ == 'coding':
            # Coding write
            reply = QMessageBox.question(self, "Write Coding", f"Update configuration for '{obj['name']}'?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.btn_run.setEnabled(False)
                self.worker = ServiceWorker(self.manager.write_coding, 0x00, obj['id'], b'\x01')
                self.worker.progress.connect(self.update_status)
                self.worker.finished.connect(self.on_finished)
                self.worker.start()

    def update_status(self, val, text):
        self.lbl_status.setText(f"[{val}%] {text}")

    def on_finished(self, success, msg):
        self.btn_run.setEnabled(True)
        self.lbl_status.setText(msg if success else f"Error: {msg}")
        if success:
            QMessageBox.information(self, "Success", msg)
