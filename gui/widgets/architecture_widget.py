from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem, 
                             QPushButton, QLabel, QGroupBox, QFileDialog, QMessageBox, QHeaderView, QSplitter, QComboBox)
from PyQt5.QtCore import Qt
from core.ingestion.vehicle_mapper import VehicleMapper
from core.ingestion.active_scanner import ActiveScanner
from core.ingestion.snapshot_scanner import SnapshotScanner
from core.repo.sync_manager import SyncManager
import os

class ArchitectureWidget(QWidget):
    def __init__(self, connection_manager=None):
        super().__init__()
        self.mapper = VehicleMapper()
        self.conn_manager = connection_manager # Need access to connection
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Vehicle Architecture & Topology")
        header.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header)
        
        # Toolbar
        toolbar = QHBoxLayout()
        self.btn_load_cfg = QPushButton("Import Config File")
        self.btn_load_cfg.clicked.connect(self.load_cfg)
        
        self.btn_load_iso = QPushButton("Import ISO Codes")
        self.btn_load_iso.clicked.connect(self.load_iso)
        
        self.btn_scan = QPushButton("Active Scan (Intrusion)")
        self.btn_scan.setStyleSheet("background-color: #ffcccc;")
        self.btn_scan.clicked.connect(self.start_scan)
        
        # Config Library Group
        grp_lib = QGroupBox("Configuration Library")
        lib_layout = QHBoxLayout()
        
        self.combo_make = QComboBox()
        self.combo_make.addItems(["Select Make...", "Jaguar", "Land Rover", "Ford", "BMW"])
        self.combo_make.currentTextChanged.connect(self.on_make_changed)
        
        self.combo_model = QComboBox()
        self.combo_model.addItem("Select Model...")
        
        self.btn_load_lib = QPushButton("Load")
        self.btn_load_lib.clicked.connect(self.load_from_library)
        self.btn_load_lib.setEnabled(False)
        
        lib_layout.addWidget(self.combo_make)
        lib_layout.addWidget(self.combo_model)
        lib_layout.addWidget(self.btn_load_lib)
        grp_lib.setLayout(lib_layout)
        
        layout.addWidget(grp_lib) # Add library selection
        
        # Export
        self.btn_export = QPushButton("Export Architecture (.json)")
        self.btn_export.clicked.connect(self.export_arch)
        
        self.btn_read_all = QPushButton("Read All Data (Snapshot)")
        self.btn_read_all.setStyleSheet("background-color: #ccffcc;")
        self.btn_read_all.clicked.connect(self.read_all_data)
        
        # Sync Group
        self.btn_pull = QPushButton("Sync/Pull")
        self.btn_pull.setToolTip("Pull updates from Community Repo")
        self.btn_pull.clicked.connect(self.pull_repo)
        
        self.btn_push = QPushButton("Share/Push")
        self.btn_push.setToolTip("Contribute this config to Community")
        self.btn_push.clicked.connect(self.push_repo)
        
        toolbar.addWidget(self.btn_load_cfg) # Keep manual load
        toolbar.addWidget(self.btn_load_iso)
        toolbar.addWidget(self.btn_scan)
        toolbar.addWidget(self.btn_read_all)
        toolbar.addWidget(self.btn_export)
        # Separator or spacer
        toolbar.addWidget(QLabel("|"))
        toolbar.addWidget(self.btn_pull)
        toolbar.addWidget(self.btn_push)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Splitter for Tree vs Details
        splitter = QSplitter(Qt.Horizontal)
        
        # Tree View
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Node / Signal", "Address / ID"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tree.itemClicked.connect(self.on_item_clicked)
        splitter.addWidget(self.tree)
        
        # Details View
        self.details_group = QGroupBox("Properties")
        v_details = QVBoxLayout()
        self.lbl_details = QLabel("Select an item to view properties.")
        self.lbl_details.setWordWrap(True)
        self.lbl_details.setAlignment(Qt.AlignTop)
        v_details.addWidget(self.lbl_details)
        self.details_group.setLayout(v_details)
        splitter.addWidget(self.details_group)
        
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)

    def load_cfg(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open Config File", "", "Config Files (*.cfg);;All Files (*)")
        if fname:
            if self.mapper.import_jlr_config(fname):
                self.refresh_tree()
                QMessageBox.information(self, "Success", f"Loaded architecture for {self.mapper.current_vehicle.name}")
            else:
                QMessageBox.warning(self, "Error", "Failed to parse config file.")

    def load_iso(self):
        dname = QFileDialog.getExistingDirectory(self, "Select Folder with ISO CSVs")
        if dname:
            import shutil
            
            # Destination
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            iso_dir = os.path.join(base_dir, 'resources', 'iso')
            os.makedirs(iso_dir, exist_ok=True)
            
            # Files to look for
            files = ['ISO14229DTCs_DTC_CODES.csv', 'ISO14229NRCs_NRC_CODES.csv', 'ISO14229DTCs_FAULT_TYPES.csv']
            copied_count = 0
            
            for f in files:
                src = os.path.join(dname, f)
                if os.path.exists(src):
                    shutil.copy2(src, os.path.join(iso_dir, f))
                    copied_count += 1
            
            # Reload
            self.mapper._auto_load_resources()
            
            if copied_count > 0:
                QMessageBox.information(self, "Success", f"Imported {copied_count} ISO definition files to internal library.")
            else:
                QMessageBox.warning(self, "Error", "No matching ISO CSV files found in selected folder.")

    def refresh_tree(self):
        self.tree.clear()
        veh = self.mapper.current_vehicle
        
        root = QTreeWidgetItem(self.tree)
        root.setText(0, veh.name or "Vehicle")
        root.setExpanded(True)
        
        # Sort ECUs by address
        sorted_ecus = sorted(veh.ecus.values(), key=lambda x: x['address'])
        
        for ecu in sorted_ecus:
            node_item = QTreeWidgetItem(root)
            node_item.setText(0, f"{ecu['name']}")
            node_item.setText(1, f"0x{ecu['address']:X}")
            node_item.setData(0, Qt.UserRole, {'type': 'ecu', 'data': ecu})
            
            # Add DIDs
            if ecu['dids']:
                did_folder = QTreeWidgetItem(node_item)
                did_folder.setText(0, "Defined DIDs")
                
                for did_id, did in ecu['dids'].items():
                    d_item = QTreeWidgetItem(did_folder)
                    
                    # Name + Value if available
                    name_text = did['name']
                    if 'last_value' in did:
                        name_text += f" = {did['last_value']}"
                        # Highlight it
                        d_item.setForeground(0, Qt.darkGreen)
                        
                    d_item.setText(0, name_text)
                    d_item.setText(1, f"0x{did_id:X}")
                    d_item.setData(0, Qt.UserRole, {'type': 'did', 'data': did})

    def start_scan(self):
        reply = QMessageBox.question(self, "Active Intrusion Warning", 
                                   "This will send 'TesterPresent' messages to range 0x700-0x7F0 on the active bus.\n"
                                   "Ensure the vehicle is capable of handling this traffic.\n\nProceed?",
                                   QMessageBox.Yes | QMessageBox.No)
                                   
        if reply == QMessageBox.Yes:
            scanner = ActiveScanner(self.conn_manager)
            
            # Simple blocking dialog for now (Thread needed in prod)
            # Using a simplified mock progress for UI responsiveness in this one-shot
            from PyQt5.QtWidgets import QProgressDialog
            pd = QProgressDialog("Scanning Network...", "Abort", 0, 100, self)
            pd.setWindowModality(Qt.WindowModal)
            pd.show()
            
            def progress(val, text):
                pd.setValue(val)
                pd.setLabelText(text)
                QApplication.processEvents()
                if pd.wasCanceled():
                    scanner.abort()
                    
            from PyQt5.QtWidgets import QApplication
            try:
                # Run Scan
                arch = scanner.scan_network(progress_callback=progress)
                if not pd.wasCanceled():
                    self.mapper.current_vehicle = arch
                    self.refresh_tree()
                    QMessageBox.information(self, "Scan Complete", f"Discovered {len(arch.ecus)} ECUs.")
            except Exception as e:
                QMessageBox.critical(self, "Scan Error", str(e))
                
            pd.close()

    def on_make_changed(self, text):
        self.combo_model.blockSignals(True)
        self.combo_model.clear()
        self.combo_model.addItem("Select Model...")
        self.combo_year.clear()
        self.combo_year.addItem("Year")
        self.btn_load_lib.setEnabled(False)
        
        if text != "Select Make...":
            models = self.repo.get_models(text)
            self.combo_model.addItems(models)
            
        self.combo_model.blockSignals(False)

    def on_model_changed(self, text):
        self.combo_year.blockSignals(True)
        self.combo_year.clear()
        self.combo_year.addItem("Year")
        
        make = self.combo_make.currentText()
        if text != "Select Model..." and make != "Select Make...":
            years = self.repo.get_years(make, text)
            self.combo_year.addItems(years)
            
        self.combo_year.blockSignals(False)

    def check_load_enable(self, text):
        valid = (self.combo_make.currentText() != "Select Make..." and
                 self.combo_model.currentText() != "Select Model..." and
                 self.combo_year.currentText() != "Year")
        self.btn_load_lib.setEnabled(valid)

    def load_from_library(self):
        make = self.combo_make.currentText()
        model = self.combo_model.currentText()
        year = self.combo_year.currentText()
        
        path = self.repo.get_config_path(make, model, year)
        
        if path and os.path.exists(path):
            success = False
            # Determine type
            if path.endswith('.cfg'):
                success = self.mapper.import_jlr_config(path)
            elif path.endswith('.json'):
                # JSON import stub
                QMessageBox.information(self, "Info", "JSON Import not fully wired yet.")
                return
                
            if success:
                self.refresh_tree()
                QMessageBox.information(self, "Success", f"Loaded {make} {model} ({year}).")
            else:
                QMessageBox.warning(self, "Error", "Failed to parse config.")
        else:
            QMessageBox.warning(self, "Error", "Config file not found in repository.")

    def read_all_data(self):
        if not self.mapper.current_vehicle.ecus:
            QMessageBox.warning(self, "Snapshot", "No architecture loaded.")
            return

        scanner = SnapshotScanner(self.conn_manager)
        
        from PyQt5.QtWidgets import QProgressDialog, QApplication
        pd = QProgressDialog("Reading Vehicle Data...", "Abort", 0, 100, self)
        pd.setWindowModality(Qt.WindowModal)
        pd.show()
        
        def progress(val, text):
            pd.setValue(val)
            pd.setLabelText(text)
            QApplication.processEvents()
            if pd.wasCanceled():
                scanner.abort()
        
        try:
            # Run Snapshot
            # The scanner modifies the architecture object in-place
            scanner.take_snapshot(self.mapper.current_vehicle, progress_callback=progress)
            
            if not pd.wasCanceled():
                self.refresh_tree()
                QMessageBox.information(self, "Snapshot Complete", "Data reading complete. Values updated.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            
        pd.close()

    def export_arch(self):
        if not self.mapper.current_vehicle.ecus:
            QMessageBox.warning(self, "Export", "No architecture loaded/scanned to export.")
            return
            
        fname, _ = QFileDialog.getSaveFileName(self, "Export Configuration", 
                                             f"{self.mapper.current_vehicle.name}.json", 
                                             "JSON Files (*.json)")
        if fname:
            from core.ingestion.vehicle_exporter import VehicleExporter
            if VehicleExporter.to_json(self.mapper.current_vehicle, fname):
                QMessageBox.information(self, "Success", f"Exported to {fname}")
            else:
                QMessageBox.critical(self, "Error", "Failed to export file.")

    def pull_repo(self):
        manager = SyncManager()
        
        from PyQt5.QtWidgets import QProgressDialog, QApplication
        pd = QProgressDialog("Syncing with Community Repo...", "Hide", 0, 100, self)
        pd.setWindowModality(Qt.WindowModal)
        pd.setWindowTitle("Repo Sync")
        pd.show()
        
        def progress(val, text):
            pd.setValue(val)
            pd.setLabelText(text)
            QApplication.processEvents()
            
        try:
            manager.pull_updates(progress_callback=progress)
            # Rescan repo to see new files
            self.repo.scan()
            self.refresh_makes()
            QMessageBox.information(self, "Sync Complete", "Successfully updated community configurations.")
        except Exception as e:
            QMessageBox.critical(self, "Sync Error", str(e))
        pd.close()

    def push_repo(self):
        if not self.mapper.current_vehicle.name or "Unknown" in self.mapper.current_vehicle.name:
            QMessageBox.warning(self, "Share", "Please load or identify a valid vehicle config first.")
            return

        reply = QMessageBox.question(self, "Contribute to Open Source", 
            f"Do you want to submit a Pull Request for '{self.mapper.current_vehicle.name}'?",
            QMessageBox.Yes | QMessageBox.No)
            
        if reply == QMessageBox.Yes:
            manager = SyncManager()
            # Mock details
            make = self.combo_make.currentText()
            model = self.combo_model.currentText()
            year = self.combo_year.currentText()
            
            from PyQt5.QtWidgets import QProgressDialog, QApplication
            pd = QProgressDialog("Submitting Pull Request...", "Hide", 0, 100, self)
            pd.setWindowModality(Qt.WindowModal)
            pd.show()
            
            def progress(val, text):
                pd.setValue(val)
                pd.setLabelText(text)
                QApplication.processEvents()
            
            try:
                manager.push_config(make, model, year, "mock_path", progress_callback=progress)
                QMessageBox.information(self, "Success", "Pull Request created successfully! #1234")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
            pd.close()

    def on_item_clicked(self, item, col):
        data = item.data(0, Qt.UserRole)
        if not data:
            self.lbl_details.setText("")
            return
            
        info = ""
        obj = data['data']
        
        if data['type'] == 'ecu':
            info += f"<b>Module:</b> {obj['name']}<br>"
            info += f"<b>Address:</b> 0x{obj['address']:X}<br>"
            info += f"<b>Network:</b> {obj['network']}<br>"
            info += f"<b>Description:</b> {obj['description']}<hr>"
            info += f"<b>Known DIDs:</b> {len(obj['dids'])}"
            
        elif data['type'] == 'did':
            info += f"<b>Signal:</b> {obj['name']}<br>"
            info += f"<b>Tag:</b> {obj['tag']}<br>"
            cmd_str = ' '.join([f"{b:02X}" for b in obj['read_cmd']])
            info += f"<b>Read Command:</b> {cmd_str}<br>"
            
        self.lbl_details.setText(info)
