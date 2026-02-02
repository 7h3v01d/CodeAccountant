# snapshot.py

import os
import shutil
import time
from config import load_config
from filetracker.utils import write_log_file  # Assuming FileTracker has a utils.py

def create_snapshot(project_folder, snapshot_dir="snapshots"):
    os.makedirs(snapshot_dir, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    snapshot_id = f"snapshot_{timestamp}"
    snapshot_path = os.path.join(snapshot_dir, snapshot_id)
    shutil.copytree(project_folder, snapshot_path, ignore=shutil.ignore_patterns(*load_config()["blacklist"]))
    log_entry = {"snapshot_id": snapshot_id, "timestamp": timestamp, "path": snapshot_path}
    write_log_file("ledger.json", log_entry)
    return snapshot_id