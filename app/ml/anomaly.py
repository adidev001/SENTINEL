# app/ml/anomaly.py

from typing import List
import numpy as np
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    """
    IsolationForest-based anomaly detector.
    """

    def __init__(self):
        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.05,
            random_state=42
        )
        self.fitted = False

    def fit(self, X: np.ndarray) -> None:
        self.model.fit(X)
        self.fitted = True

    def score(self, X: np.ndarray) -> List[int]:
        """
        Returns anomaly scores normalized to 0–100.
        Higher = more anomalous.
        """
        if not self.fitted:
            return [0 for _ in range(len(X))]

        raw_scores = -self.model.decision_function(X)
        normalized = 100 * (raw_scores - raw_scores.min()) / (
            raw_scores.max() - raw_scores.min() + 1e-6
        )
        return normalized.astype(int).tolist()
