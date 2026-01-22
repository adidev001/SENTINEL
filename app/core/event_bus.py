# app/core/event_bus.py

import asyncio
from typing import Any, Dict

class EventBus:
    """
    Central async event bus.
    Producers publish events.
    Consumers subscribe by reading queues.
    """

    def __init__(self):
        self._queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()

    async def publish(self, event: Dict[str, Any]) -> None:
        """
        Publish an event to the bus.
        """
        await self._queue.put(event)

    async def subscribe(self) -> Dict[str, Any]:
        """
        Consume the next event.
        """
        return await self._queue.get()
