from winotify import Notification, audio
import time

class AlertManager:
    """Manage system alerts and notifications."""
    
    def __init__(self):
        self.last_alert_time = {}
        self.cooldown_seconds = 60  # 1 minute cooldown per alert type
    
    def check_cooldown(self, alert_type: str) -> bool:
        """Check if alert type is in cooldown period."""
        if alert_type in self.last_alert_time:
            elapsed = time.time() - self.last_alert_time[alert_type]
            return elapsed < self.cooldown_seconds
        return False
    
    def send_windows_notification(
        self,
        title: str,
        message: str,
        severity: str = "info",
        duration: str = "short"
    ):
        """
        Send Windows toast notification.
        
        Args:
            title: Notification title
            message: Notification body
            severity: info/warning/critical
            duration: short/long
        """
        try:
            toast = Notification(
                app_id="SysSentinel AI",
                title=title,
                msg=message,
                duration=duration,
            )
            
            # Set icon based on severity
            # You can add custom icon files later
            
            # Set sound based on severity
            if severity == "critical":
                toast.set_audio(audio.LoopingAlarm, loop=False)
            elif severity == "warning":
                toast.set_audio(audio.Default, loop=False)
            
            toast.show()
            
        except Exception as e:
            print(f"Notification error: {e}")
    
    def send_webhook(self, url: str, payload: dict):
        """
        Send webhook notification.
        
        Args:
            url: Webhook URL
            payload: JSON payload
        """
        try:
            import httpx
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, json=payload)
                return response.status_code == 200
        except Exception as e:
            print(f"Webhook error: {e}")
            return False
    
    def trigger_alert(self, alert_type: str, title: str, message: str, severity: str = "info"):
        """
        Trigger an alert with cooldown check.
        
        Args:
            alert_type: Unique identifier for alert type
            title: Alert title
            message: Alert message
            severity: info/warning/critical
        """
        # Check cooldown
        if self.check_cooldown(alert_type):
            print(f"Alert {alert_type} in cooldown, skipping")
            return
        
        # Send notification
        self.send_windows_notification(title, message, severity)
        
        # Update cooldown timer
        self.last_alert_time[alert_type] = time.time()
