# app/collectors/network.py

import psutil
from typing import Dict

def collect_network() -> Dict[str, float]:
    """
    Collect network IO stats.
    """
    net = psutil.net_io_counters()
    return {
        "upload_kb": net.bytes_sent / 1024,
        "download_kb": net.bytes_recv / 1024,
    }
