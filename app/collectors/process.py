# app/collectors/process.py

import psutil
from typing import Dict, List

def collect_processes() -> List[Dict[str, float]]:
    """
    Collect per-process resource usage.
    """
    processes = []

    for proc in psutil.process_iter(attrs=["pid", "name", "cpu_percent", "memory_info"]):
        try:
            info = proc.info
            processes.append({
                "pid": info["pid"],
                "name": info["name"],
                "cpu_percent": info["cpu_percent"],
                "memory_mb": info["memory_info"].rss / (1024 * 1024)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return processes
