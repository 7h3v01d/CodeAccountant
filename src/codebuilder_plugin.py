# codebuilder_plugin.py

from filetracker.base_plugin import BasePlugin
import os

class CodeBuilderPlugin(BasePlugin):
    def process_file(self, file_path):
        if file_path.endswith(".log") and "build_logs" in file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            status = "✔" in content
            return {
                "codebuilder": {
                    "file_type": "LOG",
                    "success": status,
                    "output": content
                }
            }
        return None