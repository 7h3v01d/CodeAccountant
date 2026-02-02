# languages/python.py

import subprocess

def compile(file_path):
    return True, "Python does not require compilation."

def run(file_path):
    try:
        result = subprocess.run(["python", file_path], capture_output=True, text=True)
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)