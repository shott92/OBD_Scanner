from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QFont

class GaugeWidget(QWidget):
    def __init__(self, title="Speed", min_val=0, max_val=160, unit="mph"):
        super().__init__()
        self.title = title
        self.min_val = min_val
        self.max_val = max_val
        self.current_value = 0
        self.unit = unit
        self.setMinimumSize(200, 200)

    def set_value(self, value):
        self.current_value = max(self.min_val, min(value, self.max_val))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Coordinate setup
        side = min(self.width(), self.height())
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(side / 200.0, side / 200.0)

        # Draw Background
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(20, 20, 20))
        painter.drawEllipse(-90, -90, 180, 180)

        # Draw Ticks
        pen = QPen(QColor(200, 200, 200))
        pen.setWidth(2)
        painter.setPen(pen)
        
        start_angle = 150
        span_angle = -240 # total sweep

        for i in range(11):
            angle = start_angle + (span_angle * i / 10)
            painter.save()
            painter.rotate(angle)
            painter.drawLine(0, -80, 0, -70)
            painter.restore()

        # Draw Title and Value
        painter.setPen(Qt.white)
        font = QFont("Arial", 10)
        painter.setFont(font)
        painter.drawText(QRectF(-50, 40, 100, 20), Qt.AlignCenter, self.unit)
        
        font.setPointSize(16)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRectF(-50, 10, 100, 30), Qt.AlignCenter, str(int(self.current_value)))
        
        # Draw Title
        font.setPointSize(10)
        font.setBold(False)
        painter.setFont(font)
        painter.drawText(QRectF(-50, -50, 100, 20), Qt.AlignCenter, self.title)

        # Draw Needle
        painter.save()
        # Map value to angle
        pct = (self.current_value - self.min_val) / (self.max_val - self.min_val)
        angle = 150 + (span_angle * pct)
        
        painter.rotate(angle+90) # Adjust for 0 being 3 o'clock usually
        painter.setBrush(Qt.red)
        painter.setPen(Qt.NoPen)
        painter.drawConvexPolygon([
            # Simple needle polygon
            # Center (0,0), Tip (0, -85), Base width
        ])
        # Simple line needle for robustness first
        pen = QPen(Qt.red)
        pen.setWidth(4)
        painter.setPen(pen)
        painter.drawLine(0, 0, 0, -85)
        
        painter.restore()
