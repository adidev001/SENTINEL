# app/logic/action_router.py

from typing import Dict, List

def map_actions_to_commands(actions: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Map high-level actions to safe command identifiers.
    """
    mapped = []

    for action in actions:
        if action["type"] == "suggest_fix":
            mapped.append({
                "command_id": "analyze_top_processes",
                "requires_confirmation": False
            })

        if action["type"] == "analyze":
            mapped.append({
                "command_id": "open_analytics",
                "requires_confirmation": False
            })

    return mapped
