# app/ml/forecast.py

from typing import Dict
import numpy as np
from sklearn.linear_model import LinearRegression

class ResourceForecaster:
    """
    Linear regression forecaster for resource trends.
    """

    def __init__(self):
        self.model = LinearRegression()

    def predict(
        self,
        values: np.ndarray,
        minutes_ahead: int = 10
    ) -> Dict[str, float]:
        """Legacy method - calls predict_memory for compatibility."""
        return self.predict_memory(values, minutes_ahead)
    
    def predict_memory(
        self,
        values: np.ndarray,
        minutes_ahead: int = 10
    ) -> Dict[str, float]:
        """Predict future memory usage."""
        return self._predict_resource(values, minutes_ahead)
    
    def predict_cpu(
        self,
        values: np.ndarray,
        minutes_ahead: int = 10
    ) -> Dict[str, float]:
        """Predict future CPU usage."""
        return self._predict_resource(values, minutes_ahead)
    
    def predict_disk(
        self,
        values: np.ndarray,
        growth_rate_mb_per_min: float = 0
    ) -> Dict[str, float]:
        """
        Predict disk exhaustion time.
        
        Args:
            values: Historical disk usage percentages
            growth_rate_mb_per_min: MB written per minute (if available)
        """
        result = self._predict_resource(values, minutes_ahead=60)
        
        # Add time-to-full estimate if we have growth rate
        if growth_rate_mb_per_min > 0 and result["predicted_value"] < 100:
            space_remaining_pct = 100 - result["predicted_value"]
            # This is a simplified estimate
            result["minutes_until_full"] = (space_remaining_pct / result["predicted_value"]) * 60 if result["predicted_value"] > 0 else 9999
        else:
            result["minutes_until_full"] = 9999  # No exhaustion predicted
        
        return result
    
    def predict_network(
        self,
        values: np.ndarray,
        minutes_ahead: int = 5
    ) -> Dict[str, float]:
        """Predict future network usage (in KB/s or similar metric)."""
        return self._predict_resource(values, minutes_ahead)
    
    def _predict_resource(
        self,
        values: np.ndarray,
        minutes_ahead: int
    ) -> Dict[str, float]:
        """
        Core prediction logic used by all resource types.
        """
        if len(values) < 2:
            return {
                "predicted_value": values[-1] if len(values) else 0,
                "confidence": 0.0
            }

        X = np.arange(len(values)).reshape(-1, 1)
        y = values

        self.model.fit(X, y)

        future_x = np.array([[len(values) + minutes_ahead]])
        prediction = self.model.predict(future_x)[0]
        
        # Clamp prediction to reasonable bounds (0-100 for percentages)
        prediction = max(0, min(100, prediction))

        # crude but honest confidence proxy
        confidence = min(1.0, len(values) / 30.0)

        return {
            "predicted_value": float(prediction),
            "confidence": float(confidence)
        }

