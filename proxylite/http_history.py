from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QAbstractItemView,
    QTableWidgetItem, QSplitter, QTextEdit, QTabWidget, QMenu
)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QInputDialog, QMessageBox

from proxylite.proxy_manager import ProxyManager

class HTTPHistoryTab(QWidget):
    send_to_repeater = Signal(str)  # For future Repeater integration

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        splitter = QSplitter(Qt.Vertical)

        # Table setup
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["#", "Host", "Method", "URL", "Status"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

                
        # Set default column widths for clarity
        self.table.setColumnWidth(0, 40)    # #
        self.table.setColumnWidth(1, 240)   # Host
        self.table.setColumnWidth(2, 80)    # Method
        self.table.setColumnWidth(3, 550)   # URL
        self.table.setColumnWidth(4, 80)    # Status

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.cellClicked.connect(self.show_details)

        splitter.addWidget(self.table)

        # Details tabs
        self.details_tabs = QTabWidget()

        self.request_view = QTextEdit()
        self.request_view.setReadOnly(True)
        self.details_tabs.addTab(self.request_view, "Request")

        self.response_view = QTextEdit()
        self.response_view.setReadOnly(True)
        self.details_tabs.addTab(self.response_view, "Response")

        splitter.addWidget(self.details_tabs)
        splitter.setSizes([400, 300])

        layout.addWidget(splitter)

        # Flows storage
        self.flows = {}

        # Subscribe to ProxyManager emitter
        self.proxy_manager = ProxyManager()
        self.proxy_manager.get_emitter().intercepted.connect(self.handle_intercepted)

    def handle_intercepted(self, flow_id, data):
        updated = False

        # Update existing rows if matching ID
        for row in range(self.table.rowCount()):
            existing_flow_id = self.table.item(row, 1).data(Qt.UserRole)
            if existing_flow_id == flow_id:
                if "status" in data:
                    status_code = str(data["status"])
                    status_item = QTableWidgetItem(status_code)

                    if status_code.startswith("2"):
                        status_item.setForeground(QColor("green"))
                    elif status_code.startswith("4") or status_code.startswith("5"):
                        status_item.setForeground(QColor("red"))
                    elif status_code.startswith("3"):
                        status_item.setForeground(QColor("orange"))

                    self.table.setItem(row, 4, status_item)
                updated = True
                break

        # Store/update flows
        if "count" in data:
            self.flows[data["count"]] = data
        else:
            for key, existing_data in self.flows.items():
                if existing_data["id"] == data["id"]:
                    self.flows[key].update(data)
                    break

        # Add new row if request
        if not updated and "count" in data:
            self.add_row(flow_id, data)

    def add_row(self, flow_id, data):
        row_pos = self.table.rowCount()
        self.table.insertRow(row_pos)
        self.table.setItem(row_pos, 0, QTableWidgetItem(str(data["count"])))

        host_item = QTableWidgetItem(str(data["host"]))
        host_item.setData(Qt.UserRole, data["id"])
        self.table.setItem(row_pos, 1, host_item)

        self.table.setItem(row_pos, 2, QTableWidgetItem(str(data["method"])))
        self.table.setItem(row_pos, 3, QTableWidgetItem(str(data["url"])))

        status_code = str(data.get("status", ""))
        status_item = QTableWidgetItem(status_code)
        if status_code.startswith("2"):
            status_item.setForeground(QColor("green"))
        elif status_code.startswith("4") or status_code.startswith("5"):
            status_item.setForeground(QColor("red"))
        elif status_code.startswith("3"):
            status_item.setForeground(QColor("orange"))

        self.table.setItem(row_pos, 4, status_item)
        self.flows[data["count"]] = data

    # def show_context_menu(self, pos: QPoint):
    #     index = self.table.indexAt(pos)
    #     if index.isValid():
    #         menu = QMenu()
    #         move_action = menu.addAction("Send to Repeater")
    #         action = menu.exec(self.table.viewport().mapToGlobal(pos))
    #         if action == move_action:
    #             row = index.row()
    #             serial = int(self.table.item(row, 0).text())
    #             data = self.flows[serial]
    #             flow = data["flow"]
    #             req = flow.request

    #             raw_request = f"{req.method} {req.url} HTTP/{req.http_version}\n"
    #             for k, v in req.headers.items():
    #                 raw_request += f"{k}: {v}\n"
    #             raw_request += f"\n{req.get_text()}\n"

    #             self.send_to_repeater.emit(raw_request)

    def show_context_menu(self, pos: QPoint):
        index = self.table.indexAt(pos)
        if index.isValid():
            menu = QMenu()
            move_action = menu.addAction("Send to Repeater")
            scan_action = menu.addAction("Scan with Plugin")

            action = menu.exec(self.table.viewport().mapToGlobal(pos))
            row = index.row()
            serial = int(self.table.item(row, 0).text())
            data = self.flows[serial]
            flow = data["flow"]
            req = flow.request
            resp = flow.response

            # Build raw request text
            raw_request = f"{req.method} {req.url} HTTP/{req.http_version}\n"
            for k, v in req.headers.items():
                raw_request += f"{k}: {v}\n"
            raw_request += f"\n{req.get_text()}\n"

            if action == move_action:
                self.send_to_repeater.emit(raw_request)

            elif action == scan_action:
                # Import here to avoid circular import
                from proxylite.plugins import PluginsTab

                # Instantiate plugin manager
                plugin_tab = PluginsTab()
                plugins = plugin_tab.manager.plugins

                if not plugins:
                    QMessageBox.warning(self, "No Plugins", "No plugins are loaded to scan with.")
                    return

                # Build list of plugin names for selection
                plugin_names = [getattr(plugin, "name", plugin.__name__) for plugin in plugins]

                # Show selection dialog
                selected, ok = QInputDialog.getItem(
                    self,
                    "Select Plugin",
                    "Choose a plugin to scan this request/response:",
                    plugin_names,
                    0,
                    False
                )

                if ok and selected:
                    # Find selected plugin module
                    for plugin in plugins:
                        name = getattr(plugin, "name", plugin.__name__)
                        if name == selected:
                            selected_plugin = plugin
                            break
                    else:
                        QMessageBox.warning(self, "Plugin Not Found", "Selected plugin could not be found.")
                        return

                    # Create lightweight mock request/response objects
                    class MockRequest:
                        def __init__(self, req):
                            self.method = req.method
                            self.url = req.url
                            self.http_version = req.http_version
                            self.headers = dict(req.headers)
                            self.text = req.get_text()
                        def get_text(self):
                            return self.text

                    class MockResponse:
                        def __init__(self, resp):
                            if resp:
                                self.status_code = resp.status_code
                                self.headers = dict(resp.headers)
                                self.text = resp.get_text()
                            else:
                                self.status_code = 0
                                self.headers = {}
                                self.text = ""
                        def get_text(self):
                            return self.text

                    request = MockRequest(req)
                    response = MockResponse(resp)

                    # Run the selected plugin on this request/response
                    try:
                        selected_plugin.run(request, response)
                        QMessageBox.information(self, "Scan Complete", f"Plugin '{selected}' executed successfully on the selected request.")
                    except Exception as e:
                        QMessageBox.critical(self, "Plugin Execution Failed", f"Plugin '{selected}' failed:\n{e}")


    def show_details(self, row, col):
        serial = int(self.table.item(row, 0).text())
        data = self.flows[serial]
        flow = data["flow"]

        req = flow.request
        request_text = f"{req.method} {req.pretty_url} HTTP/{req.http_version}\n"
        for k, v in req.headers.items():
            request_text += f"{k}: {v}\n"
        request_text += f"\n{req.get_text()}\n"
        self.request_view.setPlainText(request_text)

        if flow.response:
            resp = flow.response
            response_text = f"HTTP/{resp.http_version} {resp.status_code} {resp.reason}\n"
            for k, v in resp.headers.items():
                response_text += f"{k}: {v}\n"
            response_text += f"\n{resp.get_text()}\n"
        else:
            response_text = "No response captured.\n"
        self.response_view.setPlainText(response_text)
