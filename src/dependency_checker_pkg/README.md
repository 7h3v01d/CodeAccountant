# Python Dependency Checker

A powerful **Command Line Interface (CLI)** tool to automatically scan Python project folders for missing dependencies and offer to install them. This tool helps streamline your development workflow by identifying and resolving common dependency issues.

## Features

- **Intelligent Scanning**: Detects dependencies from both `requirements.txt` files and `import` statements within Python (`.py`) files.
- **Smart Filtering**: Automatically skips built-in Python modules and local project modules (files/folders within your scanned project).
- **PyPI Name Mapping**: Handles common cases where an import name differs from its PyPI package name (e.g., `bs4` -> `beautifulsoup4`, `sklearn` -> `scikit-learn`).
- **Interactive Installation**: Prompts the user to install missing dependencies.
- **Responsive CLI**: Installation runs in a background thread, keeping the command line responsive (though visual progress is limited in a pure CLI).
- **Detailed Output**: Provides clear messages on which dependencies are checked, found, or missing.
- **Helpful Hints**: Offers specific troubleshooting tips for common installation failures (e.g., missing C++ build tools, network issues, permission errors).

## Installation

To install `python-dependency-checker` as a standalone CLI tool, follow these steps:

1. **Navigate to your project directory**:
   Open your terminal or command prompt and go to the root directory of your `dependency_checker_pkg` project (the folder containing `pyproject.toml`, `dependency_core.py`, and `dependency_cli.py`).

   ```bash
   cd /path/to/your/dependency_checker_pkg
   ```

   (Replace `/path/to/your/dependency_checker_pkg` with the actual path.)

2. **Install in editable mode (recommended for development)**:
   This allows you to make changes to the source code and have them immediately reflected when you run the `depcheck` command, without needing to reinstall.

   ```bash
   pip install -e .
   ```

3. **Verify Installation**:
   After installation, you should be able to run the `depcheck` command from any directory:

   ```bash
   depcheck --help
   ```

   This will display the help message for the tool.

## Usage

The `depcheck` tool provides `scan` and `install` commands.

### `depcheck scan`

Scans the specified folder for missing dependencies.

```bash
depcheck <path_to_project_folder> scan [options]
```

#### Arguments:

- `<path_to_project_folder>`: The path to the Python project directory you want to scan. If the path contains spaces, enclose it in double quotes (e.g., `"C:/My Project"`).

#### Options:

- `-r, --recursive`: Scan subdirectories recursively. (Default: `True`)
- `-v, --verbose`: Enable verbose output during the scan process (currently more relevant for `install` command).

#### Examples:

```bash
# Scan a project folder non-recursively
depcheck "C:/Users/YourUser/MyPythonProject" scan

# Scan a project folder recursively
depcheck "C:/Users/YourUser/MyPythonProject" -r scan
```

### `depcheck install`

Installs missing dependencies found in the specified folder. This command will first perform a scan to identify missing packages and then prompt for installation.

```bash
depcheck <path_to_project_folder> install [options]
```

#### Arguments:

- `<path_to_project_folder>`: The path to the Python project directory where you want to install dependencies. If the path contains spaces, enclose it in double quotes.

#### Options:

- `-r, --recursive`: Scan subdirectories recursively before installing. (Default: `True`)
- `-v, --verbose`: Enable verbose output during the installation process, showing more details from `pip`.

#### Examples:

```bash
# Scan and then install missing dependencies in a project folder
depcheck "C:/Users/YourUser/MyPythonProject" install

# Scan recursively and install with verbose output
depcheck "C:/Users/YourUser/MyPythonProject" -r install -v
```

## Troubleshooting Common Issues

- **SyntaxError: invalid character '�' (U+FFFD)**: This usually indicates an encoding issue with the Python script files (`dependency_core.py` or `dependency_cli.py`). Ensure these files are saved with **UTF-8 encoding (without BOM)** in your text editor.
- **Error: Python or pip command not found**: Ensure Python is correctly installed and its `Scripts` directory (which contains `pip`) is added to your system's `PATH` environment variable.
- **Microsoft Visual C++ 14.0 or greater is required**: Some Python packages (especially those with C/C++ extensions) require a compiler to be installed. On Windows, download and install **Microsoft C++ Build Tools** from [https://visualstudio.microsoft.com/visual-cpp-build-tools/](https://visualstudio.microsoft.com/visual-cpp-build-tools/). Select the "Desktop development with C++" workload during installation.
- **No matching distribution found for <package_name>**:
  - The package might not exist on PyPI under that exact name.
  - The package name might be different from the import name (e.g., `sklearn` vs. `scikit-learn`, `cv2` vs. `opencv-python`). The tool attempts to handle common mappings.
  - There might be a typo in the `requirements.txt` or `import` statement.
- **Permission denied or Access is denied**: You might not have the necessary permissions to install packages. Try running your terminal/command prompt as an **Administrator** (Windows) or using `sudo` (Linux/macOS, though generally discouraged for `pip` in virtual environments).
- **Connection aborted or Failed to establish a new connection**: Check your internet connection. If you are behind a corporate proxy, you might need to configure `pip` to use it (refer to pip documentation for proxy settings).

## Contributing

Contributions are welcome! If you find bugs, have suggestions for improvements, or want to add new features, please feel free to:

1. Fork the repository (if hosted on GitHub).
2. Create a new branch for your changes.
3. Submit a pull request.

## License

This project is licensed under the **MIT License** - see the `LICENSE` file for details (if you create one).