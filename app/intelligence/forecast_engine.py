# app/intelligence/forecast_engine.py

from typing import Dict

def interpret_forecast(
    resource: str,
    prediction: Dict[str, float],
    limit: float
) -> Dict[str, object]:
    """
    Interpret forecast output into risk information.
    """
    predicted_value = prediction.get("predicted_value", 0)
    confidence = prediction.get("confidence", 0)

    if confidence < 0.6:
        return {
            "resource": resource,
            "risk": "low",
            "confidence": confidence,
            "predicted_exhaustion": False
        }

    predicted_exhaustion = predicted_value >= limit

    risk = "high" if predicted_exhaustion else "medium"

    return {
        "resource": resource,
        "risk": risk,
        "confidence": confidence,
        "predicted_exhaustion": predicted_exhaustion
    }
