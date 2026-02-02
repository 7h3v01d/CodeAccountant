import os
import shutil
import subprocess
import tempfile
import platform
import glob
import subprocess

def compile(file_path):
    if not shutil.which("dotnet"):
        return False, ".NET SDK not found. Please install it from https://dotnet.microsoft.com."

    try:
        temp_dir = tempfile.mkdtemp()
        subprocess.run(["dotnet", "new", "console", "--output", temp_dir], check=True)

        # Replace generated Program.cs with user's file
        shutil.copy(file_path, os.path.join(temp_dir, "Program.cs"))

        # Build the project
        result = subprocess.run(["dotnet", "build", temp_dir], capture_output=True, text=True)

        # Publish as self-contained .exe
        publish_dir = os.path.join(temp_dir, "publish")
        publish_result = subprocess.run([
            "dotnet", "publish", temp_dir,
            "--configuration", "Release",
            "--output", publish_dir,
            "-r", "win-x64",
            "--self-contained", "true"
        ], capture_output=True, text=True)

        # Detect the project name from the temp dir
        project_name = os.path.basename(temp_dir)
        exe_path = os.path.join(publish_dir, f"{project_name}.exe")

        if os.path.exists(exe_path):
            os.makedirs("build_binaries", exist_ok=True)
            target_path = os.path.join("build_binaries", os.path.basename(exe_path))
            shutil.copy(exe_path, target_path)

            # Auto-open folder and select the .exe on Windows
            if platform.system() == "Windows":
                try:
                    subprocess.run(["explorer", "/select,", os.path.abspath(target_path)])
                except Exception as e:
                    publish_note += f"\n[⚠] Could not open folder: {e}"

            publish_note = f"\n[✔] Your app was published to: {target_path} and Explorer opened."
        else:
            publish_note = "\n[⚠] No matching .exe found to copy."

        success = result.returncode == 0
        output = result.stdout + result.stderr + "\n" + publish_result.stdout + publish_result.stderr + publish_note

        return success, output
    except Exception as e:
        return False, str(e)

def run(file_path):
    if not shutil.which("dotnet"):
        return False, ".NET runtime not found. Please install it from https://dotnet.microsoft.com."

    try:
        temp_dir = tempfile.mkdtemp()
        subprocess.run(["dotnet", "new", "console", "--output", temp_dir], check=True)
        shutil.copy(file_path, os.path.join(temp_dir, "Program.cs"))

        result = subprocess.run(["dotnet", "run", "--project", temp_dir], capture_output=True, text=True)

        success = result.returncode == 0
        return success, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)
