# proxylite/proxy_core.py

from PySide6.QtCore import QObject, Signal
from mitmproxy import http

class SignalEmitter(QObject):
    intercepted = Signal(str, object)  # Emit ID and data

class InterceptAddon:
    def __init__(self, emitter: SignalEmitter):
        self.emitter = emitter
        self.count = 1

    def request(self, flow: http.HTTPFlow):
        data = {
            "count": self.count,
            "id": flow.id,
            "host": flow.request.host,
            "method": flow.request.method,
            "url": flow.request.pretty_url,
            "status": flow.response.status_code if flow.response else "",
            "flow": flow
        }
        self.emitter.intercepted.emit(flow.id, data)
        self.count += 1

    def response(self, flow: http.HTTPFlow):
        data = {
            "id": flow.id,
            "status": flow.response.status_code,
            "flow": flow
        }
        self.emitter.intercepted.emit(flow.id, data)
