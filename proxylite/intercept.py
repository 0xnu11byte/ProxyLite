from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from proxylite.proxy_manager import ProxyManager
from proxylite.proxy_core import SignalEmitter


class InterceptTab(QWidget):
    send_to_repeater = Signal(str)  # For future use

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # Push Button at top-left
        self.toggle_button = QPushButton("Start Intercept")
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self.toggle_intercept)
        layout.addWidget(self.toggle_button, alignment=Qt.AlignLeft)

        # Centered messages
        self.message_container = QWidget()
        self.message_layout = QVBoxLayout(self.message_container)
        self.message_layout.setAlignment(Qt.AlignCenter)

        self.status_label = QLabel("Intercept is off")
        self.status_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.status_label.setFont(font)

        self.description_label = QLabel(
            "If you turn Intercept on, messages between ProxyLite's browser and your servers are held here. "
            "This enables you to analyze and modify these messages, before you forward them."
        )
        self.description_label.setAlignment(Qt.AlignCenter)
        self.description_label.setWordWrap(True)
        desc_font = QFont()
        desc_font.setPointSize(10)
        self.description_label.setFont(desc_font)

        self.message_layout.addWidget(self.status_label)
        self.message_layout.addWidget(self.description_label)
        layout.addWidget(self.message_container)

        # Use centralized ProxyManager
        self.proxy_manager = ProxyManager()

    def toggle_intercept(self):
        if self.toggle_button.isChecked():
            self.toggle_button.setText("Stop Intercept")
            self.status_label.setText("Intercept is on")
            self.description_label.setText(
                "Messages between ProxyLite's browser and your servers are held here. "
                "This enables you to analyze and modify these messages, before you forward them."
            )
            self.proxy_manager.start_proxy()
        else:
            self.toggle_button.setText("Start Intercept")
            self.status_label.setText("Intercept is off")
            self.description_label.setText(
                "If you turn Intercept on, messages between ProxyLite's browser and your servers are held here. "
                "This enables you to analyze and modify these messages, before you forward them."
            )
            self.proxy_manager.stop_proxy()
