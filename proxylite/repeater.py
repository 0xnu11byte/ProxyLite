# # repeater.py 
# from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QSplitter
# from PySide6.QtCore import Qt
# import requests
# import urllib3
# from urllib.parse import urlparse

# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# class RepeaterTab(QWidget):
#     def __init__(self):
#         super().__init__()
#         layout = QVBoxLayout()
#         self.setLayout(layout)

#         self.send_button = QPushButton("Send Request")
#         self.send_button.clicked.connect(self.send_request)

#         splitter = QSplitter(Qt.Horizontal)
#         self.request_editor = QTextEdit()
#         self.response_viewer = QTextEdit()
#         self.response_viewer.setReadOnly(True)

#         splitter.addWidget(self.request_editor)
#         splitter.addWidget(self.response_viewer)
#         splitter.setSizes([500, 500])

#         layout.addWidget(self.send_button)
#         layout.addWidget(splitter)


#     def send_request(self):
#         try:
#             raw = self.request_editor.toPlainText()
#             lines = raw.splitlines()
#             if not lines:
#                 self.response_viewer.setPlainText("Error: Empty request.")
#                 return

#             request_line = lines[0]
#             method, url_or_path, _ = request_line.split()

#             headers = {}
#             body_lines = []
#             in_body = False

#             for line in lines[1:]:
#                 if not in_body:
#                     if line.strip() == "":
#                         in_body = True
#                     else:
#                         if ":" in line:
#                             k, v = line.split(":", 1)
#                             headers[k.strip()] = v.strip()
#                 else:
#                     body_lines.append(line)

#             body = "\n".join(body_lines) if body_lines else None

#             parsed = urlparse(url_or_path)
#             if parsed.scheme and parsed.netloc:
#                 url = url_or_path  # full URL present
#             else:
#                 host = headers.get("Host")
#                 if not host:
#                     referer = headers.get("referer")
#                     if referer:
#                         parsed_referer = urlparse(referer)
#                         host = parsed_referer.netloc
#                         scheme = parsed_referer.scheme or "https"
#                     else:
#                         self.response_viewer.setPlainText("Error: Host header missing and no referer to infer from.")
#                         return
#                 else:
#                     scheme = "https"
#                 url = f"{scheme}://{host}{url_or_path}"

#             response = requests.request(method, url, headers=headers, data=body, verify=False)

#             resp_text = f"Status: {response.status_code}\n"
#             for k, v in response.headers.items():
#                 resp_text += f"{k}: {v}\n"
#             resp_text += "\n" + response.text
#             self.response_viewer.setPlainText(resp_text)

#         except Exception as e:
#             self.response_viewer.setPlainText(f"Error: {e}")



#     def load_request(self, raw_request):
#         self.request_editor.setPlainText(raw_request)

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QSplitter
from PySide6.QtCore import Qt
import requests
import urllib3
from urllib.parse import urlparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class RepeaterTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Container for the Send button to control alignment & width
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setAlignment(Qt.AlignLeft)  # Align button left

        self.send_button = QPushButton("Send Request")
        self.send_button.setFixedWidth(150)  # Fixed width for compact button
        self.send_button.clicked.connect(self.send_request)

        button_layout.addWidget(self.send_button)
        layout.addWidget(button_container)

        splitter = QSplitter(Qt.Horizontal)
        self.request_editor = QTextEdit()
        self.response_viewer = QTextEdit()
        self.response_viewer.setReadOnly(True)

        splitter.addWidget(self.request_editor)
        splitter.addWidget(self.response_viewer)
        splitter.setSizes([600, 600])
        splitter.setMinimumHeight(800)

        layout.addWidget(splitter)

    def send_request(self):
        try:
            raw = self.request_editor.toPlainText()
            lines = raw.splitlines()
            if not lines:
                self.response_viewer.setPlainText("Error: Empty request.")
                return

            request_line = lines[0]
            method, url_or_path, _ = request_line.split()

            headers = {}
            body_lines = []
            in_body = False

            for line in lines[1:]:
                if not in_body:
                    if line.strip() == "":
                        in_body = True
                    else:
                        if ":" in line:
                            k, v = line.split(":", 1)
                            headers[k.strip()] = v.strip()
                else:
                    body_lines.append(line)

            body = "\n".join(body_lines) if body_lines else None

            parsed = urlparse(url_or_path)
            if parsed.scheme and parsed.netloc:
                url = url_or_path  # full URL present
            else:
                host = headers.get("Host")
                if not host:
                    referer = headers.get("referer")
                    if referer:
                        parsed_referer = urlparse(referer)
                        host = parsed_referer.netloc
                        scheme = parsed_referer.scheme or "https"
                    else:
                        self.response_viewer.setPlainText("Error: Host header missing and no referer to infer from.")
                        return
                else:
                    scheme = "https"
                url = f"{scheme}://{host}{url_or_path}"

            response = requests.request(method, url, headers=headers, data=body, verify=False)

            resp_text = f"Status: {response.status_code}\n"
            for k, v in response.headers.items():
                resp_text += f"{k}: {v}\n"
            resp_text += "\n" + response.text
            self.response_viewer.setPlainText(resp_text)

        except Exception as e:
            self.response_viewer.setPlainText(f"Error: {e}")

    def load_request(self, raw_request):
        self.request_editor.setPlainText(raw_request)
