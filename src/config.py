#config.py

import json
import os

def load_config(config_path="config.json"):
    default_config = {
        "venv_path": None,
        "blacklist": [".venv", "__pycache__", "*.pyc", "build_logs", "snapshots"],
        "languages": ["python", "c", "cpp"],
        "snapshot_interval": 300  # 5 minutes
    }
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            default_config.update(config)
    return default_config

def save_config(config, config_path="config.json"):
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)