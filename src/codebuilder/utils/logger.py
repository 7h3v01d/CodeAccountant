import os
from datetime import datetime

def log(file_path, language, action, success, output):
    log_dir = "build_logs"
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = os.path.splitext(os.path.basename(file_path))[0]
    log_file = f"{name}_{action}_{timestamp}.log"
    log_path = os.path.join(log_dir, log_file)

    status = "✔" if success else "✘"

    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"[{status}] {language.upper()} {action}\n\n{output}\n")

    return log_path
