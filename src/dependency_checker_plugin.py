# dependency_checker_plugin.py

from filetracker.base_plugin import BasePlugin
from dependency_checker_pkg.dependency_core import scan_dependencies_logic

class DependencyCheckerPlugin(BasePlugin):
    def process_file(self, file_path):
        if file_path.endswith((".py", "requirements.txt")):
            missing, messages = scan_dependencies_logic(os.path.dirname(file_path))
            return {
                "dependency_checker": {
                    "file_type": "PY" if file_path.endswith(".py") else "REQ",
                    "missing_dependencies": list(missing.items()),
                    "is_missing": bool(missing)
                }
            }
        return None