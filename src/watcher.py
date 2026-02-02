# watcher.py

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from filetracker.ide_activity_monitor_plugin import FileTrackerActivityMonitor
from snapshot import create_snapshot

class Watcher(FileSystemEventHandler):
    def __init__(self, project_folder, snapshot_dir):
        self.project_folder = project_folder
        self.snapshot_dir = snapshot_dir
        self.monitor = FileTrackerActivityMonitor()

    def on_any_event(self, event):
        if event.is_directory or any(p in event.src_path for p in load_config()["blacklist"]):
            return
        self.monitor.process_file(event.src_path, event.event_type)
        create_snapshot(self.project_folder, self.snapshot_dir)

def start_watcher(project_folder, snapshot_dir="snapshots"):
    observer = Observer()
    watcher = Watcher(project_folder, snapshot_dir)
    observer.schedule(watcher, project_folder, recursive=True)
    observer.start()