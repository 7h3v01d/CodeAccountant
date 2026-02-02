# languages/java.py

import subprocess
import os
import shutil

def compile(file_path):
    if not shutil.which("javac"):
        return False, "Java compiler not found. Please install JDK and add javac to PATH."

    try:
        result = subprocess.run(["javac", file_path], capture_output=True, text=True)
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def run(file_path):
    if not shutil.which("java"):
        return False, "Java runtime not found. Please install JDK and add java to PATH."

    dir_path = os.path.dirname(file_path) or "."
    class_name = os.path.splitext(os.path.basename(file_path))[0]

    try:
        result = subprocess.run(["java", "-cp", dir_path, class_name], capture_output=True, text=True)
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)
