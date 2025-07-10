# proxylite/proxy_manager.py
from mitmproxy import options
from mitmproxy.tools.dump import DumpMaster
from proxylite.proxy_core import InterceptAddon, SignalEmitter

import threading
import asyncio
import json

class ProxyManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.master = None
        self.proxy_thread = None
        self.emitter = SignalEmitter()

    def start_proxy(self):
        if self.master:
            print("[*] Proxy already running.")
            return

        async def mitm_runner():
            with open("config/settings.json") as f:
                config = json.load(f)
            opts = options.Options(listen_host=config["proxy_host"], listen_port=config["proxy_port"])
            self.master = DumpMaster(opts, with_termlog=False, with_dumper=False)
            self.master.addons.add(InterceptAddon(self.emitter))
            await self.master.run()

        def run_in_thread():
            asyncio.run(mitm_runner())

        self.proxy_thread = threading.Thread(target=run_in_thread, daemon=True)
        self.proxy_thread.start()
        print("[*] Proxy started.")

    def stop_proxy(self):
        if self.master:
            try:
                self.master.shutdown()
                print("[*] Proxy stopped.")
            except RuntimeError:
                print("[!] Event loop already closed during shutdown.")
            self.master = None
        if self.proxy_thread and self.proxy_thread.is_alive():
            self.proxy_thread.join(timeout=1)
            self.proxy_thread = None

    def get_emitter(self):
        return self.emitter
