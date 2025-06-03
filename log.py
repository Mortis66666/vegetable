import os
import time
from datetime import datetime, timedelta

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Create a new log file with the current timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = f"{timestamp}.log"
log_path = os.path.join(LOG_DIR, log_filename)
with open(log_path, "w") as f:
    f.write(f"Log created at {timestamp}\n")

def log(*args, **kwargs):
    with open(log_path, "a") as f:
        print(*args, **kwargs, file=f)


# Remove log files older than two weeks
two_weeks_ago = datetime.now() - timedelta(weeks=2)
for fname in os.listdir(LOG_DIR):
    fpath = os.path.join(LOG_DIR, fname)
    if os.path.isfile(fpath):
        try:
            # Extract timestamp from filename
            base, ext = os.path.splitext(fname)
            file_time = datetime.strptime(base, "%Y%m%d_%H%M%S")
            if file_time < two_weeks_ago:
                os.remove(fpath)
                log(f"Removed old log file: {fname}")
        except Exception:
            # Skip files that don't match the expected format
            continue

