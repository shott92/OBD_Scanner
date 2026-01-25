from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, 
                             QFormLayout, QLabel, QLineEdit, QCheckBox, QSpinBox, 
                             QComboBox, QDialogButtonBox, QGroupBox, QScrollArea)
from PyQt5.QtCore import Qt

class AdvancedNetworkDialog(QDialog):
    def __init__(self, current_config=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Network Configuration")
        self.resize(600, 500)
        self.config = current_config or {}
        
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        
        self.tabs.addTab(self._create_transport_tab(), "Transport")
        self.tabs.addTab(self._create_timings_tab(), "Timings & Retries")
        self.tabs.addTab(self._create_routing_tab(), "Routing & Activation")
        self.tabs.addTab(self._create_vlan_tab(), "VLAN & Ethernet")
        
        layout.addWidget(self.tabs)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _create_scrollable_tab(self, layout_func):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        widget = QWidget()
        layout_func(widget)
        scroll.setWidget(widget)
        return scroll

    def _create_transport_tab(self):
        widget = QWidget()
        form = QFormLayout(widget)
        
        self.tcp_stack_combo = QComboBox()
        self.tcp_stack_combo.addItems(["Default (OS)", "Custom PCap"])
        
        self.connect_strategy_combo = QComboBox()
        self.connect_strategy_combo.addItems(["TCP_DATA_UDP_discovery", "TCP_ONLY", "UDP_ONLY"])
        
        self.source_ip = QLineEdit("0.0.0.0")
        self.listen_port = QSpinBox()
        self.listen_port.setRange(1024, 65535)
        self.listen_port.setValue(13400)
        
        self.protocol_ver = QComboBox()
        self.protocol_ver.addItems(["2012 (ISO 13400-2)", "2010 (Pre-ISO)", "2019 (Update)"])
        
        self.enable_pcap = QCheckBox("Enable PCap Logging")
        self.pcap_filter = QLineEdit("tcp port 13400")
        
        form.addRow("TCP Stack:", self.tcp_stack_combo)
        form.addRow("Connection Strategy:", self.connect_strategy_combo)
        form.addRow("Source Bind IP:", self.source_ip)
        form.addRow("Local Listener Port:", self.listen_port)
        form.addRow("Protocol Version:", self.protocol_ver)
        form.addRow(self.enable_pcap)
        form.addRow("PCap Filter:", self.pcap_filter)
        
        return widget

    def _create_timings_tab(self):
        widget = QWidget()
        form = QFormLayout(widget)
        
        self.resp_timeout = QSpinBox(); self.resp_timeout.setRange(100, 10000); self.resp_timeout.setValue(2000)
        self.ext_timeout = QSpinBox(); self.ext_timeout.setRange(1000, 300000); self.ext_timeout.setValue(5000)
        self.ack_wait = QSpinBox(); self.ack_wait.setRange(0, 5000); self.ack_wait.setValue(50)
        
        self.udp_resp_wait = QSpinBox(); self.udp_resp_wait.setRange(0, 5000); self.udp_resp_wait.setValue(500)
        
        self.nrc21_retry = QSpinBox(); self.nrc21_retry.setValue(3)
        self.reconnect_retry = QSpinBox(); self.reconnect_retry.setValue(3)
        self.discovery_retry = QSpinBox(); self.discovery_retry.setValue(1)
        
        self.socket_delay = QSpinBox(); self.socket_delay.setRange(0, 2000); self.socket_delay.setValue(50)
        
        form.addRow("Response Timeout (ms):", self.resp_timeout)
        form.addRow("Extended Timeout (ms):", self.ext_timeout)
        form.addRow("ACK Wait Time (ms):", self.ack_wait)
        form.addRow("UDP Response Wait (ms):", self.udp_resp_wait)
        form.addRow("NRC21 Retry Count:", self.nrc21_retry)
        form.addRow("Reconnection Retries:", self.reconnect_retry)
        form.addRow("Discovery Retries:", self.discovery_retry)
        form.addRow("Socket Activation Delay (ms):", self.socket_delay)
        
        return widget

    def _create_routing_tab(self):
        widget = QWidget()
        form = QFormLayout(widget)
        
        self.act_type_combo = QComboBox()
        self.act_type_combo.addItems(["Default (None)", "WWH-OBD (0x00)", "OEM Specific (0x01)"])
        
        self.oem_bytes = QLineEdit("00000000")
        self.send_activation = QCheckBox("Send Routine Activation Request")
        self.send_activation.setChecked(True)
        
        self.alive_check = QCheckBox("Unsolicited Alive Check Response")
        self.alive_check.setChecked(True)
        
        self.padding_enable = QCheckBox("Enable Padding")
        self.padding_byte = QLineEdit("CC")
        
        form.addRow("Activation Type:", self.act_type_combo)
        form.addRow("OEM Activation Bytes:", self.oem_bytes)
        form.addRow(self.send_activation)
        form.addRow(self.alive_check)
        form.addRow("Padding Statsu:", self.padding_enable)
        form.addRow("Padding Byte (Hex):", self.padding_byte)
        
        return widget

    def _create_vlan_tab(self):
        widget = QWidget()
        form = QFormLayout(widget)
        
        self.vlan_id = QSpinBox(); self.vlan_id.setRange(0, 4095); self.vlan_id.setValue(0)
        
        self.diag_prio = QSpinBox(); self.diag_prio.setRange(0, 7); self.diag_prio.setValue(0)
        self.cnc_prio = QSpinBox(); self.cnc_prio.setRange(0, 7); self.cnc_prio.setValue(0)
        
        self.subnet = QLineEdit("255.255.255.0")
        self.multicast = QLineEdit("224.0.0.1")
        
        form.addRow("VLAN ID (0=Disabled):", self.vlan_id)
        form.addRow("Diagnostic Priority:", self.diag_prio)
        form.addRow("CnC Priority:", self.cnc_prio)
        form.addRow("Subnet Mask:", self.subnet)
        form.addRow("Multicast Group:", self.multicast)
        
        return widget

    def get_settings(self):
        """Returns the configuration dict."""
        return {
            'tcp_stack': self.tcp_stack_combo.currentText(),
            'connect_strategy': self.connect_strategy_combo.currentText(),
            'source_ip': self.source_ip.text(),
            'pcap_enabled': self.enable_pcap.isChecked(),
            'timeouts': {
                'response': self.resp_timeout.value(),
                'extended': self.ext_timeout.value()
            },
            'retries': {
                'nrc21': self.nrc21_retry.value(),
                'reconnect': self.reconnect_retry.value()
            },
            'activation': {
                'type': self.act_type_combo.currentText(),
                'oem_bytes': self.oem_bytes.text()
            },
            'vlan': {
                'id': self.vlan_id.value(),
                'prio': self.diag_prio.value()
            }
        }

    def load_settings(self):
        """Populates fields from self.config if present."""
        # TODO: Implement bidirectional binding if needed for V1
        pass
