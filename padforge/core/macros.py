from __future__ import annotations

import heapq
import time
from dataclasses import dataclass, field
from typing import Callable, List


@dataclass(order=True)
class ScheduledAction:
    when: float
    order: int
    callback: Callable[[], None] = field(compare=False)


class MacroScheduler:
    """Small non-blocking scheduler. Macros never sleep inside the input loop."""

    def __init__(self) -> None:
        self._queue: List[ScheduledAction] = []
        self._order = 0

    def schedule(self, delay: float, callback: Callable[[], None]) -> None:
        self._order += 1
        heapq.heappush(self._queue, ScheduledAction(time.monotonic() + max(0.0, delay), self._order, callback))

    def tick(self) -> int:
        now = time.monotonic()
        executed = 0
        while self._queue and self._queue[0].when <= now:
            action = heapq.heappop(self._queue)
            action.callback()
            executed += 1
        return executed

    def clear(self) -> None:
        self._queue.clear()
