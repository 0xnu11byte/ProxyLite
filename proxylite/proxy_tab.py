from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from proxylite.intercept import InterceptTab
from proxylite.http_history import HTTPHistoryTab  # You will create this

class ProxyTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.intercept_tab = InterceptTab()
        self.http_history_tab = HTTPHistoryTab()

        self.tabs.addTab(self.intercept_tab, "Intercept")
        self.tabs.addTab(self.http_history_tab, "HTTP History")

        layout.addWidget(self.tabs)
