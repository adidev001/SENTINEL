# app/intelligence/health_state.py

from typing import List, Dict

def compute_health_state(
    anomalies: List[Dict[str, str]],
    forecasts: List[Dict[str, object]]
) -> Dict[str, object]:
    """
    Compute overall system health state.
    """
    state = "ok"
    contributors = []

    for anomaly in anomalies:
        if anomaly["severity"] == "critical":
            state = "critical"
            contributors.append(f"{anomaly['resource']}_anomaly")
        elif anomaly["severity"] == "warning" and state != "critical":
            state = "warning"
            contributors.append(f"{anomaly['resource']}_anomaly")

    for forecast in forecasts:
        if forecast.get("predicted_exhaustion"):
            state = "critical"
            contributors.append(f"{forecast['resource']}_forecast")

    return {
        "overall_status": state,
        "contributors": contributors
    }
