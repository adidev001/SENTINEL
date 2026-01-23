# app/ml/anomaly.py

from typing import List, Dict, Optional
import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime
import json

class AnomalyDetector:
    """
    IsolationForest-based anomaly detector with history tracking.
    """

    def __init__(self, contamination: float = 0.05, sensitivity: float = 1.0):
        """
        Args:
            contamination: Expected proportion of anomalies (0.01-0.5)
            sensitivity: Multiplier for anomaly threshold (higher = more sensitive)
        """
        self.contamination = max(0.01, min(0.5, contamination))
        self.sensitivity = sensitivity
        self.model = IsolationForest(
            n_estimators=100,
            contamination=self.contamination,
            random_state=42
        )
        self.fitted = False
        self.anomaly_threshold = 70  # Score above this triggers anomaly

    def fit(self, X: np.ndarray) -> None:
        if len(X) >= 5:  # Need minimum samples
            self.model.fit(X)
            self.fitted = True

    def score(self, X: np.ndarray) -> List[int]:
        """
        Returns anomaly scores normalized to 0–100.
        Higher = more anomalous.
        """
        if not self.fitted or len(X) == 0:
            return [0 for _ in range(len(X))]

        raw_scores = -self.model.decision_function(X)
        normalized = 100 * (raw_scores - raw_scores.min()) / (
            raw_scores.max() - raw_scores.min() + 1e-6
        )
        # Apply sensitivity multiplier
        adjusted = np.clip(normalized * self.sensitivity, 0, 100)
        return adjusted.astype(int).tolist()

    def detect_anomalies(self, X: np.ndarray, feature_names: List[str] = None) -> List[Dict]:
        """
        Detect anomalies and return detailed results.
        
        Returns list of dicts with anomaly details.
        """
        scores = self.score(X)
        anomalies = []
        
        for i, score in enumerate(scores):
            if score >= self.anomaly_threshold:
                severity = "critical" if score >= 90 else "warning" if score >= 80 else "info"
                anomalies.append({
                    "index": i,
                    "score": score,
                    "severity": severity,
                    "feature_name": feature_names[i] if feature_names and i < len(feature_names) else f"Feature_{i}"
                })
        
        return anomalies

    @staticmethod
    def save_anomaly(anomaly_type: str, severity: str, score: float, description: str, resource_values: Dict):
        """Save anomaly to database."""
        try:
            from app.storage.database import get_connection
            conn = get_connection()
            try:
                conn.execute(
                    """INSERT INTO anomaly_history 
                       (timestamp, anomaly_type, severity, score, description, resource_values) 
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        datetime.now().isoformat(),
                        anomaly_type,
                        severity,
                        score,
                        description,
                        json.dumps(resource_values)
                    )
                )
                conn.commit()
            finally:
                conn.close()
        except Exception as e:
            print(f"Error saving anomaly: {e}")

    @staticmethod
    def get_recent_anomalies(limit: int = 20) -> List[Dict]:
        """Get recent anomalies from database."""
        try:
            from app.storage.database import get_connection
            conn = get_connection()
            try:
                cur = conn.execute(
                    """SELECT * FROM anomaly_history 
                       ORDER BY timestamp DESC LIMIT ?""",
                    (limit,)
                )
                rows = cur.fetchall()
                return [dict(row) for row in rows]
            finally:
                conn.close()
        except Exception as e:
            print(f"Error reading anomalies: {e}")
            return []

