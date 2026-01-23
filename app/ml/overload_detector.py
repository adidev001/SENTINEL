# app/ml/overload_detector.py

from typing import Dict, List, Optional

class OverloadDetector:
    """
    Predicts when combined resource usage will cause system issues.
    """
    
    def predict_overload_risk(self, forecasts: Dict[str, Dict]) -> Dict:
        """
        Analyze multi-resource forecasts for overload conditions.
        
        Args:
            forecasts: Dictionary of resource forecasts from EnhancedResourceForecaster.
                       e.g. {"cpu": {"predicted_value": 80.0, ...}, ...}
                       
        Returns: {
            "risk_level": "medium",  # low, medium, high, critical
            "confidence": 0.87,
            "time_to_overload": 8.5,  # minutes (estimated)
            "primary_stressors": ["memory", "gpu"],
            "recommended_actions": ["close_browser_tabs", "reduce_gpu_load"]
        }
        """
        if not forecasts:
            return {"risk_level": "low", "confidence": 0.0}
            
        stressors = []
        max_risk_score = 0.0
        
        # Define thresholds
        thresholds = {
            "cpu": {"warn": 75, "crit": 90},
            "memory": {"warn": 80, "crit": 95},
            "disk": {"warn": 85, "crit": 95},
            "gpu": {"warn": 85, "crit": 95}
        }
        
        # Check each resource
        for res, data in forecasts.items():
            val = data.get("predicted_value", 0)
            conf = data.get("confidence", 0.5)
            
            thresh = thresholds.get(res, {"warn": 80, "crit": 90})
            
            if val >= thresh["crit"]:
                score = 1.0 * conf
                if score > 0.6:
                    stressors.append(res)
                    max_risk_score = max(max_risk_score, score)
                    
            elif val >= thresh["warn"]:
                score = 0.5 * conf
                if score > 0.3:
                    stressors.append(res)
                    max_risk_score = max(max_risk_score, score)

        # Determine overall risk
        if max_risk_score > 0.8:
            risk_level = "critical"
        elif max_risk_score > 0.6:
            risk_level = "high"
        elif max_risk_score > 0.3:
            risk_level = "medium"
        else:
            risk_level = "low"
            
        # Combine multi-resource risks (e.g. CPU + Memory is worse than just CPU)
        if len(stressors) >= 2 and risk_level in ["medium", "high"]:
            # Upgrade risk if multiple stressors
            risk_level = "high" if risk_level == "medium" else "critical"
            
        return {
            "risk_level": risk_level,
            "confidence": avg_confidence(forecasts, stressors) if stressors else 0.0,
            "primary_stressors": stressors,
            "time_to_overload": estimate_time_to_overload(forecasts, stressors)
        }

    def calculate_system_stress_index(self, forecasts: Dict) -> float:
        """
        Combined stress index (0-100) from all resource predictions.
        """
        total = 0.0
        count = 0
        for res, data in forecasts.items():
            total += data.get("predicted_value", 0)
            count += 1
        return total / count if count > 0 else 0.0


def avg_confidence(forecasts, stressors):
    if not stressors: return 0.0
    total = sum(forecasts[s].get("confidence", 0) for s in stressors)
    return total / len(stressors)

def estimate_time_to_overload(forecasts, stressors):
    # Simplified estimation: if already critical, 0. If warning, 10 min.
    # In a real model, this would use trend slope.
    if not stressors: return 999
    
    # Check if any are currently critical
    is_critical = False
    for s in stressors:
        if forecasts[s].get("predicted_value", 0) > 90:
            is_critical = True
            break
            
    return 2.0 if is_critical else 15.0
