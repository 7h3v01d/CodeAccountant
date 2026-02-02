# utils.py
import hashlib
import csv
import json
import os

def write_log_file(results, out_path, log_format="jsonl", log_hash=False, hash_algo="sha256"):
    if log_format == "jsonl":
        with open(out_path, "w", encoding="utf-8") as f:
            for record in results:
                f.write(json.dumps(record) + "\n")
    elif log_format == "csv":
        if not results:
            return
        keys = sorted(set().union(*(r.keys() for r in results)))
        with open(out_path, "w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)

    if log_hash:
        with open(out_path, "rb") as f:
            data = f.read()
            digest = hashlib.new(hash_algo, data).hexdigest()
            with open(out_path + ".hash", "w", encoding="utf-8") as hf:
                hf.write(digest + "\n")

def verify_log_hash(log_path, hash_algo="sha256"):
    hash_file = log_path + ".hash"
    if not os.path.exists(log_path) or not os.path.exists(hash_file):
        return False
    with open(log_path, "rb") as f:
        data = f.read()
        actual_hash = hashlib.new(hash_algo, data).hexdigest()
    with open(hash_file, "r", encoding="utf-8") as hf:
        expected_hash = hf.readline().strip()
    return actual_hash == expected_hash
