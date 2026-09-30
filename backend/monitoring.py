from __future__ import annotations

from collections import Counter
from datetime import datetime
from threading import Lock

class MonitoringService:
    def __init__(self):
        self._lock = Lock()
        self._events = []

    def record(self, workflow: str, status: str, details: str = ""):
        event = {
            "workflow": workflow,
            "status": status.upper(),
            "details": details,
            "occurred_at": datetime.now().isoformat(timespec="seconds"),
        }
        with self._lock:
            self._events.append(event)
            self._events = self._events[-500:]
        return event

    def summary(self):
        with self._lock:
            events = list(self._events)
        counts = Counter(event["status"] for event in events)
        return {
            "total": len(events),
            "by_status": dict(counts),
            "recent": list(reversed(events[-20:])),
        }
