# app/intelligence/anomaly_engine.py

from typing import Dict, List

def interpret_anomalies(
    scores: List[int],
    feature_names: List[str]
) -> List[Dict[str, str]]:
    """
    Convert anomaly scores into interpretable anomaly events.
    """
    events = []

    for score, feature in zip(scores, feature_names):
        if score < 50:
            continue

        if score < 70:
            severity = "yellow"
        else:
            severity = "red"

        events.append({
            "resource": feature,
            "score": score,
            "severity": severity
        })

    return events
