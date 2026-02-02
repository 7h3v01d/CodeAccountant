import argparse
import os
import sys
from .utils import detector, logger
from .languages import python, c, cpp, csharp, java, rust, go

def main():
    parser = argparse.ArgumentParser(description="CodeBuilder: Multi-language code compiler and runner")
    parser.add_argument("action", choices=["compile", "run"], help="Action to perform")
    parser.add_argument("file", help="Source file to process")
    parser.add_argument("--lang", help="Override language detection")
    args = parser.parse_args()

    file_path = os.path.abspath(args.file)
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist")
        sys.exit(1)

    lang = args.lang or detector.detect_language(file_path)
    if not lang:
        print(f"Error: Unsupported file extension for {file_path}")
        sys.exit(1)

    handlers = {
        "python": python,
        "c": c,
        "cpp": cpp,
        "csharp": csharp,
        "java": java,
        "rust": rust,
        "go": go
    }
    handler = handlers.get(lang)
    if not handler:
        print(f"Error: No handler for language {lang}")
        sys.exit(1)

    result = handler.run_action(args.action, file_path)
    logger.log_result(file_path, args.action, result)
    if result.returncode != 0:
        print(f"{args.action.capitalize()} failed: {result.stderr}")
        sys.exit(1)
    else:
        print(f"{args.action.capitalize()} successful: {result.stdout}")

if __name__ == "__main__":
    main()