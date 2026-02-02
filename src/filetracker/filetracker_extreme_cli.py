# filetracker_extreme_cli.py

import argparse
import os
import sys
import json
import importlib.util
import traceback

PLUGINS_DIR = os.path.join(os.path.dirname(__file__), "plugins")

# Dynamically load all plugins from plugins directory
def load_plugins():
    plugin_functions = []
    for fname in os.listdir(PLUGINS_DIR):
        if fname.endswith(".py") and not fname.startswith("__"):
            path = os.path.join(PLUGINS_DIR, fname)
            name = os.path.splitext(fname)[0]
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
                if hasattr(module, "extract_metadata"):
                    plugin_functions.append((name, module.extract_metadata))
            except Exception as e:
                print(f"[ERROR] Failed to load plugin {fname}: {e}")
                traceback.print_exc()
    return plugin_functions


def extract_all_metadata(file_path, selected_plugins=None):
    plugins = load_plugins()
    results = {}
    for name, func in plugins:
        if selected_plugins and name not in selected_plugins:
            continue
        try:
            result = func(file_path)
            if result:
                results[name] = result
        except Exception as e:
            results[name] = {"error": str(e)}
    return results


def main():
    parser = argparse.ArgumentParser(description="FileMetadata Extractor CLI")
    parser.add_argument('--dir', help='Directory to scan')
    parser.add_argument('--extract-metadata', action='store_true', help='Enable plugin-based metadata extraction')
    parser.add_argument('--plugin', action='append', help='Run only specific plugin(s) by name (repeatable)')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    parser.add_argument('--limit', type=int, help='Limit number of files to process')

    args = parser.parse_args()

    if not args.dir or not os.path.isdir(args.dir):
        print("[ERROR] Please provide a valid directory using --dir")
        sys.exit(1)

    files = []
    for root, _, filenames in os.walk(args.dir):
        for fname in filenames:
            full_path = os.path.join(root, fname)
            files.append(full_path)
            if args.limit and len(files) >= args.limit:
                break
        if args.limit and len(files) >= args.limit:
            break

    results = []
    for file_path in files:
        if args.extract_metadata:
            meta = extract_all_metadata(file_path, selected_plugins=args.plugin)
            results.append({"file": file_path, "metadata": meta})

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print("\n===", r.get("file", "Unknown File"), "===")
            print(json.dumps(r, indent=2))


if __name__ == '__main__':
    main()
