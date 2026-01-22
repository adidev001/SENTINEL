# app/collectors/disk.py

import psutil
from typing import Dict

def collect_disk() -> Dict[str, float]:
    """
    Collect disk usage and IO stats.
    """
    usage = psutil.disk_usage("/")
    io = psutil.disk_io_counters()

    return {
        "percent_used": usage.percent,
        "read_mb_s": io.read_bytes / (1024 * 1024),
        "write_mb_s": io.write_bytes / (1024 * 1024),
    }
