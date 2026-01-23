# app/collectors/gpu.py

from typing import Dict

def collect_gpu() -> Dict[str, float]:
    """
    Collect NVIDIA GPU stats if available.
    """
    try:
        import subprocess
        import os
        import xml.etree.ElementTree as ET

        # Determine safe subprocess flags
        startupinfo = None
        creationflags = 0
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            creationflags = subprocess.CREATE_NO_WINDOW

        # Query nvidia-smi for XML output
        # Drivers must be installed
        cmd = ["nvidia-smi", "-q", "-x"]
        
        output = subprocess.check_output(
            cmd, 
            startupinfo=startupinfo, 
            creationflags=creationflags,
            text=True
        )

        root = ET.fromstring(output)
        gpu = root.find("gpu")
        if gpu is None:
             return _empty_gpu_stats()

        # Parse memory
        fb_memory = gpu.find("fb_memory_usage")
        total_str = fb_memory.find("total").text  # e.g. "8192 MiB"
        used_str = fb_memory.find("used").text    # e.g. "450 MiB"
        
        # Parse utilization
        util = gpu.find("utilization")
        gpu_util_str = util.find("gpu_util").text # e.g. "5 %"

        def parse_val(s):
             return float(s.split()[0])

        return {
            "available": True,
            "usage_percent": parse_val(gpu_util_str),
            "memory_used_mb": parse_val(used_str),
            "memory_total_mb": parse_val(total_str)
        }
            
    except FileNotFoundError:
        # nvidia-smi not found
        return _empty_gpu_stats()
    except Exception:
        # Parsing error or other failure
        return _empty_gpu_stats()

def _empty_gpu_stats():
    return {
        "available": False, 
        "usage_percent": 0.0,
        "memory_used_mb": 0.0,
        "memory_total_mb": 0.0
    }

