from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem,
    QHBoxLayout, QMessageBox, QFileDialog, QCheckBox, QInputDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from proxylite.plugin_manager import PluginManager

import os
import shutil

class PluginsTab(QWidget):
    def __init__(self):
        super().__init__()

        self.manager = PluginManager()
        self.manager.load_plugins()

        self.plugin_states = {plugin: True for plugin in self.manager.plugins}

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # Title
        title_label = QLabel("Plugins")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignLeft)

        # Description
        desc_label = QLabel(
            "Manage and test ProxyLite plugins.\n"
            "Toggle plugins without deleting them and test their execution."
        )
        desc_label.setAlignment(Qt.AlignLeft)
        desc_label.setWordWrap(True)

        # Plugin list
        self.plugin_list = QListWidget()
        self.load_plugin_list()
        self.plugin_list.itemChanged.connect(self.toggle_plugin_state)

        # Buttons
        button_layout = QHBoxLayout()

        add_button = QPushButton("Add Plugin")
        add_button.clicked.connect(self.add_plugin)

        reload_button = QPushButton("Reload Plugins")
        reload_button.clicked.connect(self.reload_plugins)

        refresh_button = QPushButton("Refresh List")
        refresh_button.clicked.connect(self.load_plugin_list)

        test_button = QPushButton("Test Selected Plugin")
        test_button.clicked.connect(self.test_plugin)

        button_layout.addWidget(add_button)
        button_layout.addWidget(reload_button)
        button_layout.addWidget(refresh_button)
        button_layout.addWidget(test_button)

        # Add widgets to layout
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addWidget(self.plugin_list)
        layout.addLayout(button_layout)

    def load_plugin_list(self):
        """Load plugins into the QListWidget with name and description if available."""
        self.plugin_list.clear()
        self.plugin_states.clear()
        for plugin in self.manager.plugins:
            name = getattr(plugin, "name", plugin.__name__)
            description = getattr(plugin, "description", "No description provided.")
            item_text = f"{name} - {description}"

            item = QListWidgetItem(item_text)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)  # Default enabled
            item.setData(Qt.UserRole, plugin)
            self.plugin_list.addItem(item)

            self.plugin_states[plugin] = True

    def reload_plugins(self):
        """Reload plugins dynamically using PluginManager."""
        try:
            self.manager.reload_plugins()
            self.load_plugin_list()
            QMessageBox.information(self, "Plugins Reloaded", "Plugins reloaded successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Reload Failed", f"Failed to reload plugins:\n{e}")

    def add_plugin(self):
        """Open a folder selection dialog, verify, and copy the plugin folder into plugins directory."""
        folder = QFileDialog.getExistingDirectory(self, "Select Plugin Folder")
        if folder:
            if not os.path.isfile(os.path.join(folder, "__init__.py")):
                QMessageBox.warning(self, "Invalid Plugin",
                                    "Selected folder does not contain an '__init__.py'.\n"
                                    "Please select a valid plugin folder.")
                return

            plugin_name = os.path.basename(folder)
            dest_path = os.path.join(self.manager.plugin_dir, plugin_name)

            if os.path.exists(dest_path):
                QMessageBox.warning(self, "Plugin Exists",
                                    f"A plugin with the name '{plugin_name}' already exists.")
                return

            try:
                shutil.copytree(folder, dest_path)
                QMessageBox.information(self, "Plugin Added",
                                        f"Plugin '{plugin_name}' added successfully.")
                self.manager.load_plugins()
                self.load_plugin_list()
            except Exception as e:
                QMessageBox.critical(self, "Add Plugin Failed", f"Failed to add plugin:\n{e}")

    def toggle_plugin_state(self, item):
        plugin = item.data(Qt.UserRole)
        if plugin:
            enabled = item.checkState() == Qt.Checked
            self.plugin_states[plugin] = enabled
            print(f"[PluginManager] Plugin '{getattr(plugin, 'name', plugin.__name__)}' enabled: {enabled}")

    def test_plugin(self):
        """Allow the user to test a selected plugin with dummy request/response."""
        selected_items = self.plugin_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a plugin to test.")
            return

        item = selected_items[0]
        plugin = item.data(Qt.UserRole)

        if plugin not in self.plugin_states or not self.plugin_states[plugin]:
            QMessageBox.warning(self, "Plugin Disabled", "Selected plugin is currently disabled.")
            return

        # Ask user for dummy request and response data
        req_text, ok_req = QInputDialog.getText(self, "Test Plugin", "Enter dummy request data:")
        if not ok_req:
            return
        resp_text, ok_resp = QInputDialog.getText(self, "Test Plugin", "Enter dummy response data:")
        if not ok_resp:
            return

        # Create mock objects with .headers, .method, .url, etc.
        class MockRequest:
            def __init__(self, text):
                self.text = text
                self.method = "GET"
                self.url = "http://test.com"
                self.headers = {"User-Agent": "ProxyLiteTester"}
            def get_text(self):
                return self.text

        class MockResponse:
            def __init__(self, text):
                self.text = text
                self.status_code = 200
                self.headers = {"Content-Type": "text/plain"}
            def get_text(self):
                return self.text

        request = MockRequest(req_text)
        response = MockResponse(resp_text)

        try:
            plugin.run(request, response)
            QMessageBox.information(self, "Plugin Test", "Plugin executed successfully on dummy data.")
        except Exception as e:
            QMessageBox.critical(self, "Plugin Test Failed", f"Plugin execution failed:\n{e}")
