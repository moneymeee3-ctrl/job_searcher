"""EMBEDHUNT AI — Agent working memory & explainability trace.

``AgentMemory`` is an in-process, serializable record of everything the agent
observed, decided and planned during a single reasoning run. It exists so that
every autonomous recommendation can be explained after the fact ("why did the
agent tell me to apply here?") — a hard requirement for a trustworthy career
copilot.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class MemoryEntry:
    """A single timestamped step in the agent's reasoning trace."""

    phase: str
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    at: str = field(default_factory=_now)

    def to_dict(self) -> dict[str, Any]:
        return {"phase": self.phase, "message": self.message, "data": self.data, "at": self.at}


@dataclass
class AgentMemory:
    """Short-term store + ordered trace for one copilot run."""

    store: dict[str, Any] = field(default_factory=dict)
    trace: list[MemoryEntry] = field(default_factory=list)

    def remember(self, key: str, value: Any) -> None:
        """Persist a named value for later phases to read."""
        self.store[key] = value

    def recall(self, key: str, default: Any = None) -> Any:
        return self.store.get(key, default)

    def log(self, phase: str, message: str, **data: Any) -> MemoryEntry:
        """Append a step to the trace and return it."""
        entry = MemoryEntry(phase=phase, message=message, data=data)
        self.trace.append(entry)
        return entry

    @property
    def last(self) -> MemoryEntry | None:
        return self.trace[-1] if self.trace else None

    def phases(self) -> list[str]:
        return list(dict.fromkeys(e.phase for e in self.trace))

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace": [e.to_dict() for e in self.trace],
            "phases": self.phases(),
            "steps": len(self.trace),
        }
