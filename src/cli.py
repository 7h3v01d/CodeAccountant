# cli.py
import argparse
import os
import sys
import subprocess
import logging
logging.basicConfig(level=logging.DEBUG, filename="codeaccountant.log")
logging.debug(f"Running command: {sys.argv}")
try:
    from codebuilder.cli import main as codebuilder_main
except ImportError as e:
    logging.error(f"Error importing codebuilder: {e}")
    print(f"Error importing codebuilder: {e}")
    codebuilder_main = None
try:
    from python_dependency_checker.dependency_cli import main as depcheck_main
except ImportError as e:
    logging.error(f"Error importing python-dependency-checker: {e}")
    print(f"Error importing python-dependency-checker: {e}")
    depcheck_main = None
try:
    from filetracker.filetracker_cli import main as filetracker_main
except ImportError as e:
    logging.error(f"Error importing filetracker: {e}")
    print(f"Error importing filetracker: {e}")
    filetracker_main = None
from config import load_config, save_config

def main():
    parser = argparse.ArgumentParser(
        description="CodeAccountant: A private, newbie-friendly IDE for solo coders.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--config", default="config.json", help="Path to config file")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # VENV initialization
    parser_init_venv = subparsers.add_parser("init-venv", help="Initialize a VENV for the project folder")
    parser_init_venv.add_argument("folder", help="Project folder path")

    # Dependency commands
    parser_deps = subparsers.add_parser("deps", help="Manage dependencies")
    deps_subparsers = parser_deps.add_subparsers(dest="deps_command")
    parser_deps_check = deps_subparsers.add_parser("check", help="Check for missing dependencies and compilers")
    parser_deps_check.add_argument("folder", help="Project folder path")
    parser_deps_check.add_argument("-r", "--recursive", action="store_true", help="Scan recursively")
    parser_deps_check.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser_deps_install = deps_subparsers.add_parser("install", help="Install missing dependencies")
    parser_deps_install.add_argument("folder", help="Project folder path")
    parser_deps_install.add_argument("-r", "--recursive", action="store_true", help="Scan recursively")
    parser_deps_install.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    # Build/run commands
    parser_build = subparsers.add_parser("build", help="Compile a source file")
    parser_build.add_argument("file", help="Source file path")
    parser_build.add_argument("--lang", help="Override language detection")
    parser_run = subparsers.add_parser("run", help="Run a source file")
    parser_run.add_argument("file", help="Source file path")
    parser_run.add_argument("--lang", help="Override language detection")

    # Import command
    parser_import = subparsers.add_parser("import", help="Clone a GitHub repository")
    parser_import.add_argument("repo_url", help="GitHub repository URL")

    # Analyze command
    parser_analyze = subparsers.add_parser("analyze", help="Run forensic analysis on snapshots/files")
    parser_analyze.add_argument("folder", help="Project folder path")
    parser_analyze.add_argument("--pii", action="store_true", help="Check for sensitive data")
    parser_analyze.add_argument("--compare", nargs=2, metavar=("snapshot1", "snapshot2"), help="Compare two snapshots")

    args = parser.parse_args()
    config = load_config(args.config)

    if args.command == "init-venv":
        if not os.path.exists(args.folder):
            os.makedirs(args.folder)
        print(f"Initializing VENV in {args.folder}...")
        venv_path = os.path.join(args.folder, ".venv")
        subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
        config["venv_path"] = venv_path
        save_config(config)
        print(f"VENV initialized at {venv_path}")
        sys.exit(0)

    elif args.command == "deps":
        if not depcheck_main:
            logging.error("python-dependency-checker not installed")
            print("Error: python-dependency-checker not installed")
            sys.exit(1)
        depcheck_args = [args.deps_command, args.folder]
        if args.recursive:
            depcheck_args.append("--recursive")
        if args.verbose:
            depcheck_args.append("--verbose")
        sys.argv = ["depcheck"] + depcheck_args
        depcheck_main()

    elif args.command in ("build", "run"):
        if not codebuilder_main:
            logging.error("CodeBuilder not installed")
            print("Error: CodeBuilder not installed")
            sys.exit(1)
        sys.argv = ["codebuilder", args.command, args.file]
        if args.lang:
            sys.argv.extend(["--lang", args.lang])
        codebuilder_main()

    elif args.command == "import":
        print(f"Importing repository {args.repo_url}...")
        # To be implemented with github_fetcher.py and snapshot.py
        sys.exit(0)

    elif args.command == "analyze":
        if not filetracker_main:
            logging.error("FileTracker not installed")
            print("Error: FileTracker not installed")
            sys.exit(1)
        sys.argv = ["filetracker", "analyze", args.folder]
        if args.pii:
            sys.argv.append("--pii")
        if args.compare:
            sys.argv.extend(["--compare"] + args.compare)
        filetracker_main()

    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()