from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QTextEdit

class LogWidget(QGroupBox):
    def __init__(self, title="Interaction Log"):
        super().__init__(title)
        layout = QVBoxLayout()
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)
        self.setLayout(layout)

    def append_message(self, message):
        self.log_box.append(message)
