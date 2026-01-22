# app/logic/decision_engine.py

from typing import List, Dict

def decide_actions(
    health_state: Dict[str, object],
    anomalies: List[Dict[str, str]],
    forecasts: List[Dict[str, object]]
) -> Dict[str, object]:
    """
    Decide what actions should be taken based on system state.
    """
    actions = []

    if health_state["overall_status"] == "green":
        return {
            "notify": False,
            "actions": actions
        }

    if health_state["overall_status"] == "yellow":
        actions.append({
            "type": "analyze",
            "reason": "System instability detected"
        })

    if health_state["overall_status"] == "red":
        actions.append({
            "type": "notify",
            "reason": "High risk of system failure"
        })
        actions.append({
            "type": "suggest_fix",
            "reason": "Preventative action recommended"
        })

    return {
        "notify": health_state["overall_status"] in ("yellow", "red"),
        "actions": actions
    }
