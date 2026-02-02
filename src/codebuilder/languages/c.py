#languages/c.py

import subprocess
import os
import shutil

def compile(file_path):
    if not shutil.which("gcc"):
        return False, "GCC compiler not found. Please install GCC and add it to PATH."

    binary = os.path.splitext(file_path)[0]
    if os.name == 'nt':
        binary += '.exe'

    try:
        result = subprocess.run(["gcc", file_path, "-o", binary], capture_output=True, text=True)
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def run(file_path):
    binary = os.path.splitext(file_path)[0]
    if os.name == 'nt':
        binary += '.exe'

    if not os.path.exists(binary):
        return False, "Compiled binary not found. Please compile first."

    try:
        result = subprocess.run([binary], capture_output=True, text=True)
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)
