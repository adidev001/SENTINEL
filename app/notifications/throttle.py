# app/notifications/throttle.py

import time

class NotificationThrottle:
    """
    Simple throttle to prevent notification spam.
    """

    def __init__(self, cooldown_seconds: int = 300):
        self.cooldown = cooldown_seconds
        self._last_sent = 0.0

    def allow(self) -> bool:
        now = time.time()
        if now - self._last_sent >= self.cooldown:
            self._last_sent = now
            return True
        return False
