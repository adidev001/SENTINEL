# app/core/scheduler.py

import asyncio
from typing import Callable, Awaitable

class Scheduler:
    """
    Lightweight async scheduler for periodic jobs.
    """

    def __init__(self):
        self._tasks = []

    def every(self, interval_seconds: int, job: Callable[[], Awaitable[None]]) -> None:
        """
        Schedule a recurring async job.
        """
        async def _runner():
            while True:
                try:
                    await job()
                except Exception as e:
                    print(f"Scheduler job failed: {e}")
                await asyncio.sleep(interval_seconds)

        self._tasks.append(asyncio.create_task(_runner()))

    def cancel_all(self) -> None:
        """
        Cancel all scheduled jobs.
        """
        for task in self._tasks:
            task.cancel()
