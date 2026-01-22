# app/ml/features.py

from typing import Dict, List
import numpy as np

FEATURE_ORDER = [
    "cpu_percent",
    "memory_percent",
    "disk_percent",
    "read_mb",
    "write_mb",
    "upload_kb",
    "download_kb",
]

def extract_features(metric: Dict[str, float]) -> np.ndarray:
    """
    Convert a metric dict into a fixed-order feature vector.
    Missing values default to 0.
    """
    return np.array(
        [metric.get(key, 0.0) for key in FEATURE_ORDER],
        dtype=float
    )

def batch_features(metrics: List[Dict[str, float]]) -> np.ndarray:
    """
    Convert a list of metric dicts into a feature matrix.
    """
    return np.vstack([extract_features(m) for m in metrics])
