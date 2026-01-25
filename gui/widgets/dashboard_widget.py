from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel
from .gauge_widget import GaugeWidget

class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QGridLayout(self)
        
        # Gauges
        self.speed_gauge = GaugeWidget("Speed", 0, 160, "mph")
        self.rpm_gauge = GaugeWidget("RPM", 0, 8000, "rpm")
        
        self.layout.addWidget(self.speed_gauge, 0, 0)
        self.layout.addWidget(self.rpm_gauge, 0, 1)

        # Performance Stats
        self.perf_label = QLabel("0-60: Ready")
        self.perf_label.setStyleSheet("font-size: 18px; color: #00FF00; font-weight: bold;")
        self.layout.addWidget(self.perf_label, 1, 0, 1, 2)

    def update_data(self, name, value_str):
        # Extremely basic parsing for demo
        # "123 mph" -> 123
        try:
            val = float(value_str.split(' ')[0])
            if "Vehicle Speed" in name or "Speed" in name:
                self.speed_gauge.set_value(val)
            elif "Engine RPM" in name or "RPM" in name:
                self.rpm_gauge.set_value(val)
        except:
            pass
            
    def update_perf_status(self, status_text):
        self.perf_label.setText(status_text)
