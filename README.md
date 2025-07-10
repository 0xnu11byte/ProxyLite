# ProxyLite
![logo](proxylite/assets/proxylite_logo.png)
---
**ProxyLite** is a lightweight Burp Repeater alternative with:

✅ Intercept tab (live HTTP/HTTPS request capture)

✅ Repeater tab (craft/send requests, view responses)

✅ Clean, modular, open-source architecture

✅ Built using PySide6, mitmproxy, requests

## Usage
1. Install dependencies:
```
pip install -r requirements.txt
```
2. Run ProxyLite:
```
python proxylite.py
```
3. Set your browser/system proxy to `127.0.0.1:8080`.
4. Use Intercept/Repeater tabs for workflow.

## Features
- Live intercept using mitmproxy
- Request crafting and sending
- Response viewing
- Modular for future extensions
