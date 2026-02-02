# tests/test_integration.py

import unittest
from codebuilder.cli import main as codebuilder_main
from dependency_checker_pkg.dependency_core import scan_dependencies_logic

class TestIntegration(unittest.TestCase):
    def test_codebuilder_python(self):
        sys.argv = ["codebuilder", "run", "test.py"]
        codebuilder_main()  # Ensure no crash

    def test_dependency_checker(self):
        missing, messages = scan_dependencies_logic("test_project")
        self.assertIsInstance(missing, dict)
        self.assertIsInstance(messages, list)

if __name__ == "__main__":
    unittest.main()