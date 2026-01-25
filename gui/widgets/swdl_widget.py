from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QGroupBox, QFileDialog, QProgressBar, QTextEdit, QMessageBox,
                             QDialog, QComboBox, QListWidget, QInputDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from core.swdl.parsers.vbf_parser import VBFParser
from core.swdl.parsers.bin_parser import BinParser
from core.swdl.parsers.sgo_parser import SGOParser
from core.swdl.sequence_engine import SequenceEngine
from core.repo.firmware_repo import FirmwareRepository
import os

class SWDLWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, engine, vbf):
        super().__init__()
        self.engine = engine
        self.vbf = vbf
        
    def run(self):
        try:
            self.engine.run_sequence(self.vbf, self.report_progress)
            self.finished.emit(True, "Flash Completed Successfully")
        except Exception as e:
            self.finished.emit(False, str(e))
            
    def report_progress(self, val, text):
        self.progress.emit(val, text)

class RepoSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Flash File from Repository")
        self.repo = FirmwareRepository()
        self.selected_path = None
        
        layout = QVBoxLayout(self)
        
        # Make
        layout.addWidget(QLabel("Make:"))
        self.cbo_make = QComboBox()
        self.cbo_make.addItems(self.repo.get_makes())
        self.cbo_make.currentTextChanged.connect(self.on_make_changed)
        layout.addWidget(self.cbo_make)
        
        # Model
        layout.addWidget(QLabel("Model:"))
        self.cbo_model = QComboBox()
        layout.addWidget(self.cbo_model)
        self.cbo_model.currentTextChanged.connect(self.on_model_changed)
        
        # ECU
        layout.addWidget(QLabel("ECU:"))
        self.cbo_ecu = QComboBox()
        layout.addWidget(self.cbo_ecu)
        self.cbo_ecu.currentTextChanged.connect(self.on_ecu_changed)
        
        # File List
        layout.addWidget(QLabel("Available VBF/Binaries:"))
        self.list_files = QListWidget()
        layout.addWidget(self.list_files)
        
        # Buttons
        btns = QHBoxLayout()
        btn_ok = QPushButton("Load")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_ok)
        btns.addWidget(btn_cancel)
        layout.addLayout(btns)
        
        # Init
        if self.cbo_make.count() > 0:
            self.on_make_changed(self.cbo_make.currentText())

    def on_make_changed(self, text):
        self.cbo_model.clear()
        self.cbo_model.addItems(self.repo.get_models(text))
        
    def on_model_changed(self, text):
        self.cbo_ecu.clear()
        make = self.cbo_make.currentText()
        if make and text:
            self.cbo_ecu.addItems(self.repo.get_ecus(make, text))

    def on_ecu_changed(self, text):
        self.list_files.clear()
        make = self.cbo_make.currentText()
        model = self.cbo_model.currentText()
        if make and model and text:
            files = self.repo.get_files(make, model, text)
            for f in files:
                item = f"{f['filename']} ({f['type']}) - {f['notes']}"
                self.list_files.addItem(item)
    
    def accept(self):
        row = self.list_files.currentRow()
        if row < 0: return
        
        # Get filename
        text = self.list_files.currentItem().text()
        filename = text.split(' ')[0]
        
        make = self.cbo_make.currentText()
        model = self.cbo_model.currentText()
        ecu = self.cbo_ecu.currentText()
        
        self.selected_path = self.repo.get_file_path(make, model, ecu, filename)
        super().accept()

class SWDLWidget(QWidget):
    def __init__(self, connection_manager=None):
        super().__init__()
        self.conn = connection_manager
        self.vbf = None
        self.engine = None
        self.worker = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Software Download (SWDL)")
        header.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header)
        
        # File Selection
        grp_file = QGroupBox("Flash File Selection")
        hbox = QHBoxLayout()
        self.lbl_file = QLabel("No file selected")
        btn_browse = QPushButton("Browse .vbf")
        btn_browse.clicked.connect(self.browse_file)
        
        btn_repo = QPushButton("Load from Library")
        btn_repo.clicked.connect(self.load_from_repo)
        
        hbox.addWidget(self.lbl_file)
        hbox.addWidget(btn_browse)
        hbox.addWidget(btn_repo)
        grp_file.setLayout(hbox)
        layout.addWidget(grp_file)
        
        # Info Panel
        self.txt_info = QTextEdit()
        self.txt_info.setReadOnly(True)
        self.txt_info.setPlaceholderText("File information will appear here...")
        self.txt_info.setMaximumHeight(100)
        layout.addWidget(self.txt_info)
        
        # Execution
        grp_exec = QGroupBox("Flash Execution")
        vbox = QVBoxLayout()
        
        self.pbar = QProgressBar()
        self.lbl_status = QLabel("Ready")
        
        self.btn_start = QPushButton("Start Download")
        self.btn_start.setStyleSheet("background-color: #ffcccc; font-weight: bold;") # Red warning
        self.btn_start.clicked.connect(self.start_download)
        self.btn_start.setEnabled(False)
        
        vbox.addWidget(self.lbl_status)
        vbox.addWidget(self.pbar)
        vbox.addWidget(self.btn_start)
        grp_exec.setLayout(vbox)
        layout.addWidget(grp_exec)
        
        # Log
        layout.addWidget(QLabel("Execution Log:"))
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        layout.addWidget(self.txt_log)

    def parse_firmware(self, fname):
        self.log(f"Parsing {fname}...")
        
        ext = os.path.splitext(fname)[1].lower()
        parser = None
        
        if ext == '.vbf':
            parser = VBFParser(fname)
        elif ext == '.bin':
            parser = BinParser(fname)
        elif ext == '.sgo' or ext == '.frf':
            parser = SGOParser(fname)
        
        if parser and parser.parse():
            self.vbf = parser # Rename var later, keeping 'vbf' for ABI compat for now
            self.lbl_file.setText(os.path.basename(fname))
            
            info = "<b>Firmware Info:</b><br>"
            for k, v in parser.header.items():
                info += f"{k}: {v}<br>"
            info += f"Blocks: {len(parser.blocks)}<br>"
            
            self.txt_info.setHtml(info)
            self.btn_start.setEnabled(True)
            self.log("Parse Successful.")
        else:
            self.log("Parse Failed or Unknown Format.")
            QMessageBox.critical(self, "Error", "Failed to parse firmware file.")

    def load_from_repo(self):
        dlg = RepoSelectionDialog(self)
        if dlg.exec_() == QDialog.Accepted and dlg.selected_path:
            self.parse_firmware(dlg.selected_path)

    def browse_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open Firmware", "", "Supported Files (*.vbf *.bin *.sgo *.frf);;All Files (*)")
        if fname:
            self.parse_firmware(fname)

    def start_download(self):
        if not self.vbf: return
        
        reply = QMessageBox.warning(self, "Confirm Flash", 
            "WARNING: Flashing can brick the ECU if interrupted.\nEnsure battery is stable.\n\nProceed?",
            QMessageBox.Yes | QMessageBox.No)
            
        if reply == QMessageBox.Yes:
            self.log("Initializing Flash Sequence...")
            self.btn_start.setEnabled(False)
            
            self.engine = SequenceEngine(self.conn)
            self.worker = SWDLWorker(self.engine, self.vbf)
            self.worker.progress.connect(self.on_progress)
            self.worker.finished.connect(self.on_finished)
            self.worker.start()

    def on_progress(self, val, text):
        self.pbar.setValue(val)
        self.lbl_status.setText(text)
        self.log(f"[{val}%] {text}")

    def on_finished(self, success, msg):
        self.btn_start.setEnabled(True)
        if success:
            QMessageBox.information(self, "Flash Complete", msg)
            self.log("SUCCESS: " + msg)
        else:
            QMessageBox.critical(self, "Flash Failed", msg)
            self.log("ERROR: " + msg)
        
        self.pbar.setValue(0)
        self.lbl_status.setText("Ready")

    def log(self, msg):
        self.txt_log.append(msg)
