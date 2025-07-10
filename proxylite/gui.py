import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from proxylite.proxy_tab import ProxyTab
from proxylite.repeater import RepeaterTab
from proxylite.about import AboutTab  # Ensure the filename is about_tab.py
from proxylite.plugins import PluginsTab

def launch_gui():
    app = QApplication(sys.argv)
    window = ProxyLiteWindow()
    window.show()
    sys.exit(app.exec())

class ProxyLiteWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ProxyLite")
        self.resize(1000, 700)

        icon = QIcon("assets/icon.png")
        self.setWindowIcon(icon)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Load Tabs
        self.proxy_tab = ProxyTab()
        self.repeater_tab = RepeaterTab()
        self.about_tab = AboutTab()
        self.plugins_tab = PluginsTab()

        # # Plugins Placeholder
        # self.plugins_tab = QWidget()
        # plugins_layout = QVBoxLayout(self.plugins_tab)
        # plugins_label = QLabel("Plugins coming soon.")
        # plugins_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        # plugins_layout.addWidget(plugins_label)

        # Add Tabs
        self.tabs.addTab(self.proxy_tab, "Proxy")
        self.tabs.addTab(self.repeater_tab, "Repeater")
        self.tabs.addTab(self.plugins_tab, "Plugins")
        self.tabs.addTab(self.about_tab, "About")

        # Connect HTTPHistoryTab signals to RepeaterTab
        self.proxy_tab.http_history_tab.send_to_repeater.connect(self.repeater_tab.load_request)

