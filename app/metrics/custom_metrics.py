import json
import os
from datetime import datetime
from typing import List, Dict

CUSTOM_METRICS_FILE = "custom_metrics.json"

class CustomMetricsManager:
    """Manage user-defined custom metrics."""
    
    def __init__(self):
        self.metrics = self.load_metrics()
    
    def load_metrics(self) -> List[Dict]:
        """Load custom metric definitions."""
        if os.path.exists(CUSTOM_METRICS_FILE):
            try:
                with open(CUSTOM_METRICS_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def save_metrics(self):
        """Save custom metric definitions."""
        try:
            with open(CUSTOM_METRICS_FILE, 'w') as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            print(f"Error saving custom metrics: {e}")
    
    def add_metric(self, name: str, metric_type: str, command: str, interval: int = 60):
        """
        Add a custom metric.
        
        Args:
            name: Metric name
            metric_type: Type (counter/gauge/histogram)
            command: Command to execute or Python expression
            interval: Collection interval in seconds
        """
        metric = {
            "id": len(self.metrics) + 1,
            "name": name,
            "type": metric_type,
            "command": command,
            "interval": interval,
            "enabled": True,
            "created_at": datetime.now().isoformat()
        }
        self.metrics.append(metric)
        self.save_metrics()
        return metric
    
    def remove_metric(self, metric_id: int):
        """Remove a custom metric."""
        self.metrics = [m for m in self.metrics if m.get("id") != metric_id]
        self.save_metrics()
    
    def toggle_metric(self, metric_id: int):
        """Enable/disable a custom metric."""
        for metric in self.metrics:
            if metric.get("id") == metric_id:
                metric["enabled"] = not metric.get("enabled", True)
                self.save_metrics()
                break
    
    def get_enabled_metrics(self) -> List[Dict]:
        """Get all enabled metrics."""
        return [m for m in self.metrics if m.get("enabled", True)]
    
    def collect_metric_value(self, metric: Dict) -> float:
        """
        Collect current value for a metric.
        
        Returns the metric value or 0 if collection fails.
        """
        try:
            command = metric.get("command", "")
            
            # If it's a Python expression, evaluate it
            if command.startswith("python:"):
                code = command.replace("python:", "").strip()
                # Safe evaluation context
                import psutil
                context = {"psutil": psutil}
                result = eval(code, context)
                return float(result)
            
            # Otherwise execute as shell command
            import subprocess
            result = subprocess.check_output(command, shell=True, text=True)
            return float(result.strip())
            
        except Exception as e:
            print(f"Error collecting metric {metric.get('name')}: {e}")
            return 0.0
