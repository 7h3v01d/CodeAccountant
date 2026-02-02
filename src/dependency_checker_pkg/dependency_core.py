import os
import subprocess
import re
import sys
import builtins

# --- Configuration Data ---
# A comprehensive list of standard library modules to skip.
# All entries are converted to lowercase for robust matching.
STANDARD_LIBRARY_MODULES = set(sys.builtin_module_names) | {
    "os", "sys", "json", "re", "math", "datetime", "logging", "collections", "io",
    "subprocess", "threading", "pathlib", "functools", "abc", "typing", "warnings",
    "itertools", "urllib", "http", "ftplib", "smtplib", "poplib", "nntplib",
    "imaplib", "email", "xml", "csv", "zipfile", "tarfile", "shutil", "tempfile",
    "mimetypes", "time", "hashlib", "inspect", "decimal", "fractions", "random",
    "statistics", "array", "heapq", "queue", "socket", "ssl", "selectors",
    "asyncio", "unittest", "doctest", "pdb", "venv", "ensurepip", "distutils",
    "setuptools", "site", "idlelib", "tkinter", "sqlite3", "concurrent", "traceback",
    "argparse", "importlib", "wave", "uuid",
    "_thread", "_tkinter", "winreg", "msvcrt", "nt",
    "lib2to3", "configparser", "decimal", "ftplib", "gzip", "locale", "multiprocessing",
    "optparse", "queue", "socketserver", "ssl", "string", "struct", "tempfile", "termios",
    "textwrap", "timeit", "tty", "unicodedata", "warnings", "webbrowser", "xmlrpc", "zipapp",
}
# Convert all to lowercase to ensure case-insensitive checking for standard modules
STANDARD_LIBRARY_MODULES = {m.lower() for m in STANDARD_LIBRARY_MODULES}


# Mappings for common import names to PyPI package names
PACKAGE_NAME_MAP = {
    "bs4": "beautifulsoup4",
    "PIL": "Pillow",
    "cv2": "opencv-python",
    "sklearn": "scikit-learn",
    "osgeo": "gdal",
    "magic": "python-magic", # Often needs system libmagic too
    "lxml": "lxml", # Sometimes misidentified due to underlying C libs
    "pycrypto": "pycryptodome", # Common rename
    "Crypto": "pycryptodome", # Common rename
    # Add more as you discover them
}

# --- Core Functions ---

def _run_pip_command(command_args):
    """
    Helper to run a pip command and capture its output.
    Returns (returncode, stdout, stderr).
    """
    try:
        process = subprocess.run(
            [sys.executable, '-m', 'pip'] + command_args,
            capture_output=True,
            text=True,
            check=False, # Do not raise an exception for non-zero exit codes
            encoding='utf-8', errors='ignore'
        )
        return process.returncode, process.stdout, process.stderr
    except FileNotFoundError:
        return 1, "", "Error: Python or pip command not found. Ensure Python and pip are installed and in your PATH."
    except Exception as e:
        return 1, "", f"An unexpected error occurred while running pip: {e}"


def check_package_installed(package_name, package_name_map=None):
    """
    Checks if a package is installed. Uses common mappings for import names
    that differ from PyPI names.
    """
    if package_name_map is None:
        package_name_map = PACKAGE_NAME_MAP

    # First, try the exact package name
    returncode, stdout, stderr = _run_pip_command(['show', package_name])
    if returncode == 0 and "Name:" in stdout:
        return True

    # If not found, try common mapped names
    mapped_name = package_name_map.get(package_name)
    if mapped_name:
        returncode, stdout, stderr = _run_pip_command(['show', mapped_name])
        if returncode == 0 and "Name:" in stdout:
            return True

    return False

def extract_imports_from_file(file_path):
    """
    Extracts top-level module names from import statements in a Python file.
    This handles 'import foo' and 'from foo import bar'.
    It does NOT handle dynamic imports, conditional imports, or relative imports.
    """
    imported_modules = set()
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                # Match 'import module_name'
                match_import = re.match(r'^\s*import\s+([a-zA-Z0-9_.]+)', line)
                if match_import:
                    module_name = match_import.group(1).split('.')[0]
                    imported_modules.add(module_name)
                    continue

                # Match 'from module_name import something'
                match_from_import = re.match(r'^\s*from\s+([a-zA-Z0-9_.]+)\s+import', line)
                if match_from_import:
                    module_name = match_from_import.group(1).split('.')[0]
                    # Exclude relative imports (e.g., from . import utils)
                    if not module_name.startswith('.'):
                        imported_modules.add(module_name)

    except Exception as e:
        # In a module, we might log this or pass it up, but for CLI, print is okay
        print(f"  Warning: Could not parse {file_path} for imports: {e}")
    return imported_modules

def scan_dependencies_logic(folder_path, recursive=True, standard_lib_modules=None, package_name_map=None):
    """
    Scans a folder for Python files and requirements.txt to identify dependencies.
    Returns a tuple: (missing_dependencies_dict, scan_summary_messages)
    missing_dependencies_dict: {module_name: source_info}
    scan_summary_messages: list of strings for detailed output.
    """
    if standard_lib_modules is None:
        standard_lib_modules = STANDARD_LIBRARY_MODULES
    if package_name_map is None:
        package_name_map = PACKAGE_NAME_MAP

    missing_dependencies = {}
    scan_summary_messages = []
    found_dependencies_to_check = False

    scan_summary_messages.append(f"Scanning folder: {folder_path}")

    walk_generator = os.walk(folder_path)
    if not recursive:
        try:
            root, dirs, files = next(walk_generator)
            walk_generator = [(root, dirs, files)]
        except StopIteration:
            scan_summary_messages.append("\nSelected folder is empty or contains no relevant files.")
            return missing_dependencies, scan_summary_messages

    for root, _, files in walk_generator:
        for file in files:
            # 1. Check for requirements.txt files
            if file == 'requirements.txt':
                found_dependencies_to_check = True
                req_file_path = os.path.join(root, file)
                scan_summary_messages.append(f"\n--- Checking '{file}' ({os.path.relpath(req_file_path, folder_path)}) ---")
                try:
                    with open(req_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                package_name = re.split(r'[<>=~]', line)[0].strip()
                                if package_name:
                                    scan_summary_messages.append(f"  Checking '{package_name}'...")
                                    if not check_package_installed(package_name, package_name_map):
                                        display_name = package_name_map.get(package_name, package_name)
                                        missing_dependencies[package_name] = f'requirements.txt ({os.path.relpath(req_file_path, folder_path)})'
                                        scan_summary_messages.append(f"  ❌ Missing: {display_name}")
                                    else:
                                        display_name = package_name_map.get(package_name, package_name)
                                        scan_summary_messages.append(f"  ✅ Installed: {display_name}")
                except Exception as e:
                    scan_summary_messages.append(f"  Error reading {req_file_path}: {e}")

            # 2. Check for .py files for import statements
            elif file.endswith('.py'):
                py_file_path = os.path.join(root, file)
                if file == '__init__.py' and os.path.getsize(py_file_path) < 50:
                    continue

                found_dependencies_to_check = True
                scan_summary_messages.append(f"\n--- Checking '{file}' ({os.path.relpath(py_file_path, folder_path)}) for imports ---")
                imported_modules = extract_imports_from_file(py_file_path)

                for module in imported_modules:
                    module_lower = module.lower()

                    # Skip built-in/standard library modules (case-insensitive check)
                    if module_lower in standard_lib_modules:
                        scan_summary_messages.append(f"  (Skipping built-in/standard: {module})")
                        continue

                    # Heuristic for local project modules: check if a .py file or folder exists
                    is_local_module = False
                    # Check in the root of the selected project folder
                    if os.path.exists(os.path.join(folder_path, module + '.py')) or \
                       os.path.exists(os.path.join(folder_path, module)):
                        is_local_module = True
                    # Also check relative to the current file's directory (for deeper nested modules)
                    elif os.path.exists(os.path.join(root, module + '.py')) or \
                         os.path.exists(os.path.join(root, module)):
                        is_local_module = True

                    if is_local_module:
                        scan_summary_messages.append(f"  (Skipping local module: {module})")
                        continue

                    # Check if it's installed using the refined method
                    display_module_name = package_name_map.get(module, module)
                    scan_summary_messages.append(f"  Checking '{display_module_name}' (from import)...")
                    if not check_package_installed(module, package_name_map):
                        if module not in missing_dependencies:
                            missing_dependencies[module] = f'import in {os.path.relpath(py_file_path, folder_path)}'
                            scan_summary_messages.append(f"  ❌ Missing: {display_module_name}")
                    else:
                        scan_summary_messages.append(f"  ✅ Installed: {display_module_name}")

    if not found_dependencies_to_check and not missing_dependencies:
        scan_summary_messages.append("\nNo 'requirements.txt' files or Python files with significant imports found in the selected directory.")
    elif missing_dependencies:
        scan_summary_messages.append("\n--- Scan Complete ---")
        scan_summary_messages.append("\nSummary of Missing Dependencies:")
        for pkg, src in missing_dependencies.items():
            display_pkg_name = package_name_map.get(pkg, pkg)
            scan_summary_messages.append(f"- {display_pkg_name} (from {src})")
    else:
        scan_summary_messages.append("\n--- Scan Complete ---")
        scan_summary_messages.append("\nAll detected dependencies are installed! �")

    return missing_dependencies, scan_summary_messages


def install_dependencies_logic(missing_dependencies, package_name_map=None, verbose=False):
    """
    Performs pip installations for missing dependencies.
    Returns a tuple: (successful_installs, failed_installs, installation_messages)
    """
    if package_name_map is None:
        package_name_map = PACKAGE_NAME_MAP

    installation_messages = []
    successful_installs = []
    failed_installs = []

    if not missing_dependencies:
        installation_messages.append("No missing dependencies to install.")
        return successful_installs, failed_installs, installation_messages

    installation_messages.append("\n--- Starting Installation ---")

    packages_to_install_pypi_names = [package_name_map.get(pkg, pkg) for pkg in list(missing_dependencies.keys())]
    original_missing_keys = list(missing_dependencies.keys())

    for i, pypi_package_name in enumerate(packages_to_install_pypi_names):
        original_module_name = original_missing_keys[i]

        installation_messages.append(f"Installing '{pypi_package_name}'...")
        if verbose:
            print(f"DEBUG: Attempting to install: {pypi_package_name}") # For console output

        returncode, stdout, stderr = _run_pip_command(['install', pypi_package_name])

        if returncode == 0:
            installation_messages.append(f"  ✅ Successfully installed: {pypi_package_name}")
            successful_installs.append(pypi_package_name)
        else:
            error_output = stderr
            # Provide specific guidance for common errors
            if "Microsoft Visual C++ 14.0 or greater is required" in error_output:
                error_output += "\n  (HINT: Install Microsoft C++ Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/)"
            elif "The 'sklearn' PyPI package is deprecated, use 'scikit-learn'" in error_output:
                error_output += "\n  (HINT: Use 'scikit-learn' instead of 'sklearn'.)"
            elif "You were probably trying to install `gdal` by running `pip install osgeo`" in error_output:
                error_output += "\n  (HINT: Use 'gdal' instead of 'osgeo'.)"
            elif "No matching distribution found for" in error_output:
                error_output += "\n  (HINT: This package might not exist on PyPI, or its name is different, or it has specific build requirements.)"
            elif "Permission denied" in error_output or "Access is denied" in error_output:
                error_output += "\n  (HINT: Try running your terminal/command prompt as Administrator.)"
            elif "Connection aborted" in error_output or "Failed to establish a new connection" in error_output:
                error_output += "\n  (HINT: Check your internet connection or proxy settings.)"


            installation_messages.append(f"  ❌ Failed to install {pypi_package_name}:\n{error_output}")
            failed_installs.append(pypi_package_name)
        
        if verbose:
            print(f"DEBUG: Installation of {pypi_package_name} finished with return code {returncode}") # For console output


    installation_messages.append("\n--- Installation Summary ---")
    if successful_installs:
        installation_messages.append(f"Successfully installed: {', '.join(successful_installs)}")
    if failed_installs:
        installation_messages.append(f"Failed to install: {', '.join(failed_installs)}")
    else:
        installation_messages.append("All missing dependencies installed successfully! ✨")

    return successful_installs, failed_installs, installation_messages

if __name__ == "__main__":
    # This block is for testing the core logic directly
    # It will not open a GUI.
    print("--- Testing dependency_core.py directly ---")
    test_folder = os.getcwd() # Or specify a test folder path
    print(f"Scanning current directory: {test_folder}")

    # Example: Create a dummy file for testing
    if not os.path.exists("test_project_for_core"):
        os.makedirs("test_project_for_core")
    with open("test_project_for_core/script.py", "w") as f:
        f.write("import requests\nfrom bs4 import BeautifulSoup\nimport numpy\nimport os\n")
    with open("test_project_for_core/requirements.txt", "w") as f:
        f.write("pandas\nscipy\n")

    missing, scan_output = scan_dependencies_logic("test_project_for_core", recursive=True)
    for msg in scan_output:
        print(msg)

    if missing:
        print("\nAttempting to install missing dependencies...")
        success, failed, install_output = install_dependencies_logic(missing, verbose=True)
        for msg in install_output:
            print(msg)
    else:
        print("\nNo missing dependencies found in test_project_for_core.")

    # Clean up dummy files
    # import shutil
    # shutil.rmtree("test_project_for_core")
