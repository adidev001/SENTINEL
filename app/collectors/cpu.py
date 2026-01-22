# app/collectors/cpu.py

import psutil
from typing import Dict

def collect_cpu() -> Dict[str, float]:
    """
    Collect CPU usage percentage.
    """
    return {
        "cpu_percent": psutil.cpu_percent(interval=None)
    }
