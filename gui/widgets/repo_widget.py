from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QPushButton, QLabel, QInputDialog, QMessageBox, QGroupBox, QFileDialog)
from core.session.protocol_manager import ProtocolManager
from core.session.db_manager import DBManager
import os

class RepoWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.proto_manager = ProtocolManager()
        self.db_manager = DBManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("Protocol & DBC Repository")
        header.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header)

        # List Area
        list_layout = QHBoxLayout()
        
        # We'll split the view: Protocols (JSON) and databases (DBC)
        self.pkg_list = QListWidget()
        self.pkg_list.itemClicked.connect(self.on_pkg_clicked)
        
        self.dbc_list = QListWidget()
        self.dbc_list.itemClicked.connect(self.on_dbc_clicked)

        list_layout.addWidget(QLabel("Vehicle Packages:"))
        list_layout.addWidget(self.pkg_list)
        list_layout.addWidget(QLabel("DBC Files:"))
        list_layout.addWidget(self.dbc_list)
        
        # Details / Actions
        actions_layout = QVBoxLayout()
        self.btn_create = QPushButton("Create New Package")
        self.btn_create.clicked.connect(self.create_package)
        
        self.btn_import_dbc = QPushButton("Import DBC File")
        self.btn_import_dbc.clicked.connect(self.import_dbc)
        
        self.btn_download = QPushButton("Download from OpenDBC")
        self.btn_download.clicked.connect(self.download_opendbc)

        actions_layout.addWidget(self.btn_create)
        actions_layout.addWidget(self.btn_import_dbc)
        actions_layout.addWidget(self.btn_download)
        actions_layout.addStretch()
        
        list_layout.addLayout(actions_layout)
        layout.addLayout(list_layout)

        # Details Panel
        self.details_group = QGroupBox("Details")
        self.details_label = QLabel("Select an item to view details.")
        v = QVBoxLayout()
        v.addWidget(self.details_label)
        self.details_group.setLayout(v)
        layout.addWidget(self.details_group)

        self.refresh_list()

    def refresh_list(self):
        self.pkg_list.clear()
        packages = self.proto_manager.list_packages()
        self.pkg_list.addItems(packages)
        
        self.dbc_list.clear()
        dbcs = self.db_manager.list_available_dbcs()
        for tier, files in dbcs.items():
            for f in files:
                self.dbc_list.addItem(f"{f} [{tier}]")

    def create_package(self):
        name, ok = QInputDialog.getText(self, "New Package", "Package Name:")
        if ok and name:
            try:
                self.proto_manager.create_package(name, "Local User Package")
                self.refresh_list()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
    
    def import_dbc(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open DBC File', '', "DBC Files (*.dbc)")
        if fname:
            try:
                self.db_manager.import_dbc_file(fname, "local")
                self.refresh_list()
                QMessageBox.information(self, "Success", "DBC imported to Local tier.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def download_opendbc(self):
        # Fetch file list from GitHub API
        try:
            import requests
            # Correct path is now opendbc/dbc
            url = "https://api.github.com/repos/commaai/opendbc/contents/opendbc/dbc"
            response = requests.get(url)
            if response.status_code == 200:
                files = [f['name'] for f in response.json() if f['name'].endswith('.dbc')]
                
                item, ok = QInputDialog.getItem(self, "Download OpenDBC", 
                                              "Select a DBC file to download:", 
                                              files, 0, False)
                if ok and item:
                    # Download the raw file from the new path
                    raw_url = f"https://raw.githubusercontent.com/commaai/opendbc/master/opendbc/dbc/{item}"
                    r = requests.get(raw_url)
                    if r.status_code == 200:
                        # Save to opendbc tier
                        save_path = os.path.join(self.db_manager.tiers['opendbc'], item)
                        with open(save_path, 'wb') as f:
                            f.write(r.content)
                        self.refresh_list()
                        QMessageBox.information(self, "Success", f"Downloaded {item} from OpenDBC.")
                    else:
                         QMessageBox.warning(self, "Error", "Failed to download file content.")
            else:
                QMessageBox.warning(self, "Error", f"Failed to fetch catalog: {response.status_code}")
                
        except ImportError:
             QMessageBox.critical(self, "Error", "The 'requests' library is missing. Please install it.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def on_pkg_clicked(self, item):
        name = item.text()
        data = self.proto_manager.load_package(name)
        if data:
            self.details_label.setText(f"Type: Protocol Package\nName: {data.get('name')}\nVersion: {data.get('version')}")

    def on_dbc_clicked(self, item):
        text = item.text()
        # Parse "filename.dbc [tier]"
        filename = text.split(' [')[0]
        self.details_label.setText(f"Type: CAN Database\nFile: {filename}\nSource: {text.split(' [')[1][:-1]}")
