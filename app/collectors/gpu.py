# app/collectors/gpu.py

from typing import Dict
import GPUtil

def collect_gpu() -> Dict[str, float]:
    """
    Collect NVIDIA GPU stats if available.
    """
    gpus = GPUtil.getGPUs()
    if not gpus:
        # Fallback for systems without dedicated NVIDIA GPU
        # Return 0.0 so the graph has data, even if it's just "0%"
        return {
            "available": True, 
            "usage_percent": 0.0,
            "memory_used_mb": 0.0,
            "memory_total_mb": 0.0
        }

    gpu = gpus[0]
    return {
        "available": True,
        "usage_percent": gpu.load * 100,
        "memory_used_mb": gpu.memoryUsed,
        "memory_total_mb": gpu.memoryTotal
    }

