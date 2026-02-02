# utils/github_fetcher.py

import tempfile
import subprocess
import os

def fetch_repo(repo_url):
    tmp_dir = tempfile.mkdtemp()
    try:
        subprocess.run(["git", "clone", repo_url, tmp_dir], check=True)
        print(f"[FETCH] Cloned repo to {tmp_dir}")
    except subprocess.CalledProcessError:
        print("[ERROR] Failed to clone repository")
        return None
    return tmp_dir
