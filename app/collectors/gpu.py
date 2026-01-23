# app/collectors/gpu.py

from typing import Dict

def collect_gpu() -> Dict[str, float]:
    """
    Collect NVIDIA GPU stats if available.
    """
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        if not gpus:
            # Fallback for systems without dedicated NVIDIA GPU
            return _empty_gpu_stats()

        gpu = gpus[0]
        return {
            "available": True,
            "usage_percent": gpu.load * 100,
            "memory_used_mb": gpu.memoryUsed,
            "memory_total_mb": gpu.memoryTotal
        }
    except Exception:
        # Graceful fallback if GPUtil fails or no drivers
        return _empty_gpu_stats()

def _empty_gpu_stats():
    return {
        "available": False, 
        "usage_percent": 0.0,
        "memory_used_mb": 0.0,
        "memory_total_mb": 0.0
    }

