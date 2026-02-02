# plugin_loader.py
import importlib.util
import os
import sys
import traceback

PLUGIN_DIRECTORY = os.path.join(os.path.dirname(__file__), "plugins")

class PluginRegistry:
    def __init__(self):
        self.metadata_extractors = []
        self.custom_matchers = {}

    def register_metadata_extractor(self, func):
        self.metadata_extractors.append(func)

    def register_matcher(self, name, func):
        self.custom_matchers[name] = func

def register_all_plugins(plugin_registry):
    print("⚠️ Responsible Use Reminder: Use plugins only on authorized data.")
    load_plugins(plugin_registry)

def load_plugins(registry: PluginRegistry):
    if not os.path.exists(PLUGIN_DIRECTORY):
        return

    for filename in os.listdir(PLUGIN_DIRECTORY):
        if not filename.endswith(".py") or filename.startswith("__"):
            continue
        plugin_path = os.path.join(PLUGIN_DIRECTORY, filename)
        module_name = f"plugins.{filename[:-3]}"

        try:
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            if hasattr(module, "register"):
                module.register(registry)
        except Exception as e:
            print(f"[PLUGIN ERROR] Failed to load {filename}:\n{traceback.format_exc()}")
