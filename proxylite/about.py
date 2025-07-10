from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt

class AboutTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)  # Reduce spacing between widgets

        # Load and display the image (adjust path accordingly)
        pixmap = QPixmap("proxylite/assets/proxylite_logo.png")
        if not pixmap.isNull():
            pixmap = pixmap.scaledToWidth(300, Qt.SmoothTransformation)  # Slightly smaller for balance
        else:
            print("[!] Warning: AboutTab logo image failed to load.")

        image_label = QLabel()
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)

        # Title label
        title_label = QLabel("ProxyLite v1.0")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)

        # Creator label
        creator_label = QLabel("Created by 0xNU11BYTE")
        creator_font = QFont()
        creator_font.setPointSize(10)
        creator_label.setFont(creator_font)
        creator_label.setAlignment(Qt.AlignCenter)

        # Description label
        desc_label = QLabel(
            "ProxyLite is a lightweight, modular intercepting proxy tool for web security enthusiasts.\n"
            "Capture, inspect, and replay HTTP requests seamlessly."
        )
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_font = QFont()
        desc_font.setPointSize(10)
        desc_label.setFont(desc_font)

        # Add widgets to layout
        layout.addWidget(image_label)
        layout.addWidget(title_label)
        layout.addWidget(creator_label)
        layout.addWidget(desc_label)
