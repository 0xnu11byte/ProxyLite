# ProxyLite
![logo](proxylite/assets/proxylite_logo.png)
---
# ProxyLite

ProxyLite is an open-source, lightweight HTTP/HTTPS proxy and request tester designed for security researchers, penetration testers, and developers. It combines a clean, modular architecture built with PySide6 and mitmproxy, offering both usability and powerful extensibility.

## Key Features

- **Traffic Capture Module:**  
  Monitor and capture live HTTP and HTTPS requests and responses in real-time, with full inspection and modification capabilities.

- **Request Crafting Console:**  
  Build, edit, and resend HTTP requests effortlessly to probe APIs, web applications, or services, and immediately analyze the responses.

- **Plugin-Friendly:**  
  Extend ProxyLite’s core with custom plugins—create your own testing, exploitation, or automation tools easily.

- **Modern UI:**  
  Intuitive PySide6-based interface with a clean, user-friendly design optimized for productivity.

- **Flexible Architecture:**  
  Seamlessly integrates with popular Python libraries like mitmproxy and requests, making scripting and automation straightforward.

---

ProxyLite empowers users to quickly discover vulnerabilities, debug web services, and experiment with HTTP traffic — all within a lightweight and customizable framework.


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
