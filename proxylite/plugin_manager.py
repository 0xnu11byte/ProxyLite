import os
import importlib.util
import importlib

class PluginManager:
    def __init__(self, plugin_dir="proxylite/plugins"):
        self.plugin_dir = plugin_dir
        self.plugins = []

    def load_plugins(self):
        self.plugins = []  # Clear existing plugins before loading
        for item in os.listdir(self.plugin_dir):
            path = os.path.join(self.plugin_dir, item)
            if os.path.isdir(path):
                init_path = os.path.join(path, "__init__.py")
                if os.path.isfile(init_path):
                    spec = importlib.util.spec_from_file_location(item, init_path)
                    module = importlib.util.module_from_spec(spec)
                    try:
                        spec.loader.exec_module(module)
                        self.plugins.append(module)
                        print(f"[PluginManager] Loaded plugin package: {module.name}")
                    except Exception as e:
                        print(f"[PluginManager] Failed to load {item}: {e}")
            elif item.endswith(".py"):
                spec = importlib.util.spec_from_file_location(item[:-3], path)
                module = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(module)
                    self.plugins.append(module)
                    print(f"[PluginManager] Loaded plugin: {module.name}")
                except Exception as e:
                    print(f"[PluginManager] Failed to load {item}: {e}")

    def reload_plugins(self):
        print("[PluginManager] Reloading plugins...")
        for i, module in enumerate(self.plugins):
            try:
                importlib.reload(module)
                print(f"[PluginManager] Reloaded plugin: {module.name}")
            except Exception as e:
                print(f"[PluginManager] Failed to reload {module.__name__}: {e}")

    def run_plugins(self, request, response):
        for plugin in self.plugins:
            try:
                plugin.run(request, response)
            except Exception as e:
                print(f"[PluginManager] Error running {plugin.name}: {e}")
