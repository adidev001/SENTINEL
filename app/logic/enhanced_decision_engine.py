# app/logic/enhanced_decision_engine.py

from typing import Dict, List, Optional
from app.logic.decision_engine import decide_actions
from app.notifications.rules import should_notify

def enhanced_decide_actions(
    health_state: Dict,
    anomalies: List,
    forecasts: List,
    overload_predictions: Dict = None
) -> Dict:
    """
    Enhanced decision engine with overload prediction support.
    
    Backward compatible: If overload_predictions is None,
    behaves exactly like existing decide_actions().
    """
    
    # 1. Get base decisions
    base_decision = decide_actions(health_state, anomalies, forecasts)
    actions = base_decision.get("actions", [])
    
    # 2. Add Overload-specific actions
    if overload_predictions:
        risk_level = overload_predictions.get("risk_level")
        stressors = overload_predictions.get("primary_stressors", [])
        
        if risk_level in ["high", "critical"]:
            actions.append({
                "type": "prevent_overload",
                "reason": f"High overload risk detected ({', '.join(stressors)})",
                "urgency": "immediate" if risk_level == "critical" else "high",
                "metadata": overload_predictions
            })
        elif risk_level == "medium":
            actions.append({
                "type": "monitor_overload",
                "reason": "Moderate overload risk",
                "urgency": "soon",
                "metadata": overload_predictions
            })
    
    # 3. Enhanced notification logic
    # We might want to force notification if risk is high
    notify = base_decision.get("notify", False)
    if overload_predictions and overload_predictions.get("risk_level") in ["high", "critical"]:
        notify = True
    
    return {
        "notify": notify,
        "actions": actions,
        "overload_risk": overload_predictions.get("risk_level", "unknown") if overload_predictions else "unknown",
        "health_state": health_state
    }
