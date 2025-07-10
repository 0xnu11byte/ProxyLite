#!/usr/bin/env python3

import os
import sys
from datetime import datetime

PLUGIN_DIR = "proxylite/plugins"

TEMPLATE_INIT = """# {plugin_name}/__init__.py

name = "{name}"
description = "{description}"
author = "{author}"

def run(request, response):
    try:
        print(f"[{name}] Running on request to {{request.url}}")
        # Add your plugin logic here
    
        except Exception as e:
            print(f"[{name}] Error: {{e}}")
"""

TEMPLATE_UTILS = '''# {plugin_name}/utils.py

def example_helper():
    # Example helper function from utils.py
'''

EXAMPLE_PAYLOAD = '''# Example payloads for your plugin
PAYLOAD_1
PAYLOAD_2
PAYLOAD_3
'''

def create_plugin(plugin_name, author="0xYourHandle", description="A ProxyLite plugin"):
    plugin_path = os.path.join(PLUGIN_DIR, plugin_name)

    if os.path.exists(plugin_path):
        print(f"[!] Plugin '{plugin_name}' already exists.")
        return
    
    os.makedirs(plugin_path)
    os.makedirs(os.path.join(plugin_path, "payloads"))

    with open(os.path.join(plugin_path, "__init__.py"), "w") as f:
        f.write(TEMPLATE_INIT.format(
            plugin_name = plugin_name,
            name = plugin_name.replace("_", " ").title(),
            description = description,
            author = author
        ))
    
    with open(os.path.join(plugin_path, "utils.py"), "w") as f:
        f.write(TEMPLATE_UTILS.format(plugin_name = plugin_name))

    with open(os.path.join(plugin_path, "payloads", "example_payloads.txt"), "w") as f:
        f.write(EXAMPLE_PAYLOAD)
    
    print(f"[+] Plugin '{plugin_name}' created successfully at '{plugin_path}'")

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_plugin.py <plugin_name> [author] [description]")
        sys.exit(1)
    
    plugin_name = sys.argv[1]
    author = sys.argv[2] if len(sys.argv) > 2 else "0xYourHandle"
    description = sys.argv[3] if len(sys.argv) > 3 else "a ProxyLite plugin"

    create_plugin(plugin_name, author, description)

if __name__ == "__main__":
    main()