# languages/go.py

import subprocess
import os
import shutil

def compile(file_path):
    if not shutil.which("go"):
        return False, "Go compiler not found. Please install Go and add it to PATH."

    output_binary = os.path.splitext(file_path)[0]
    if os.name == 'nt':
        output_binary += '.exe'

    try:
        result = subprocess.run(["go", "build", "-o", output_binary, file_path], capture_output=True, text=True)
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

