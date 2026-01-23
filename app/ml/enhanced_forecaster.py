# app/ml/enhanced_forecaster.py

from typing import Dict, List, Optional
import numpy as np
from app.ml.forecast import ResourceForecaster

class EnhancedResourceForecaster(ResourceForecaster):
    """
    Multi-resource forecasting engine that extends the base forecaster.
    Provides simultaneous warnings for CPU, Memory, Disk, and Network usage.
    """
    
    def __init__(self, history_size: int = 30):
        super().__init__()
        self.history_size = history_size
        # We can maintain separate internal forecasters if needed, 
        # or share the underlying model logic.
        # For simplicity and robustness, we reuse the base logic per resource.
    
    def predict_all_resources(self, metrics_history: List[Dict]) -> Dict[str, Dict]:
        """
        Predict future usage for all available resources.
        
        Args:
            metrics_history: List of metric dictionaries from storage.
            
        Returns:
            Dictionary mapping resource name to prediction details.
            Example:
            {
                "cpu": {"predicted_value": 45.2, "confidence": 0.85},
                "memory": {"predicted_value": 78.9, "confidence": 0.92},
                ...
            }
        """
        if not metrics_history:
            return {}
            
        predictions = {}
        
        # Resources to forecast
        resources = {
            "cpu": "cpu_percent",
            "memory": "memory_percent",
            "disk": "disk_percent",
            "gpu": "gpu_percent"
        }
        
        for res_name, key in resources.items():
            # Extract series
            series = [
                m.get(key) for m in metrics_history 
                if m.get(key) is not None
            ]
            
            if len(series) < 5:
                continue
                
            try:
                # Use base class predict method
                result_dict = self.predict(series)
                predicted_val = result_dict.get("predicted_value", 0.0)
                
                # Simple confidence estimation based on variance
                # (Lower variance = higher confidence)
                if len(series) > 1:
                    variance = np.var(series[-5:])  # Last 5 points
                    confidence = max(0.0, 1.0 - (variance / 100.0))
                else:
                    confidence = 0.5
                
                predictions[res_name] = {
                    "predicted_value": max(0.0, min(100.0, predicted_val)), # Clamp 0-100
                    "confidence": float(f"{confidence:.2f}")
                }
                
            except Exception as e:
                # Log error but don't crash whole forecast
                print(f"Forecast error for {res_name}: {e}")
                
        return predictions
