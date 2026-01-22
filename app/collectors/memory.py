# app/collectors/memory.py

import psutil
from typing import Dict

def collect_memory() -> Dict[str, float]:
    """
    Collect memory usage stats.
    """
    mem = psutil.virtual_memory()
    return {
        "used_mb": mem.used / (1024 * 1024),
        "total_mb": mem.total / (1024 * 1024),
        "percent": mem.percent
    }
