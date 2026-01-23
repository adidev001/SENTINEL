# app/intelligence/overload_engine.py

from typing import Dict

def interpret_overload_prediction(
    overload_data: Dict,
    current_metrics: Dict = None
) -> Dict:
    """
    Convert raw overload predictions into actionable insights.
    
    Returns: {
        "summary": "System at risk of memory overload in 8 minutes",
        "explanation": "...",
        "confidence": "high",
        "prevention_steps": [...],
        "auto_prevention_available": True
    }
    """
    if not overload_data or overload_data.get("risk_level") == "low":
        return None
        
    risk = overload_data["risk_level"]
    stressors = overload_data.get("primary_stressors", [])
    time_to = overload_data.get("time_to_overload", 999)
    
    # Generate Summary
    if risk == "critical":
        summary = f"CRITICAL: System overload imminent in {time_to:.1f} min"
    elif risk == "high":
        summary = f"High risk of {', '.join(stressors)} overload"
    else:
        summary = f"Potential {', '.join(stressors)} issues detected"
        
    # Explanation
    explanation = f"Forecasts indicate {', '.join(stressors)} usage will exceed safe limits."
    
    # Prevention Steps
    steps = []
    if "memory" in stressors:
        steps.append("Close unused browser tabs")
        steps.append("Check for memory leaks in background apps")
    if "cpu" in stressors:
        steps.append("Reduce background processing")
    if "gpu" in stressors:
        steps.append("Pause GPU-intensive rendering")
        
    return {
        "summary": summary,
        "explanation": explanation,
        "confidence": overload_data.get("confidence", 0.0),
        "prevention_steps": steps,
        "auto_prevention_available": False # Placeholder for future auto-kill features
    }
