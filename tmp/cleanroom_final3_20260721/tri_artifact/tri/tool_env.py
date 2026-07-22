from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolEnvironment:
    """Small stateful tool environment for TRI tasks."""

    task: dict
    refreshed: bool = False
    processed_target: str | None = None
    trace: list[dict[str, Any]] = field(default_factory=list)

    @property
    def current_state(self) -> list[dict]:
        return self.task["refreshed_state"] if self.refreshed else self.task["initial_state"]

    def observe(self) -> dict:
        result = {
            "ok": True,
            "tool": "observe",
            "refreshed": self.refreshed,
            "entities": self.current_state,
        }
        self.trace.append({"tool": "observe", "result": result})
        return result

    def refresh(self) -> dict:
        self.refreshed = True
        result = {
            "ok": True,
            "tool": "refresh",
            "refreshed": True,
            "entities": self.current_state,
        }
        self.trace.append({"tool": "refresh", "result": result})
        return result

    def process(self, target_id: str | None) -> dict:
        self.processed_target = target_id
        if target_id == "INVALID_BOUND_ENTITY":
            ok = self.task["correct_target"] == "INVALID_BOUND_ENTITY"
            result = {
                "ok": ok,
                "tool": "process",
                "target_id": target_id,
                "status": "invalid_bound_entity" if ok else "invalid_target_requested",
            }
        else:
            present = any(item["id"] == target_id for item in self.current_state)
            result = {
                "ok": present,
                "tool": "process",
                "target_id": target_id,
                "status": "processed" if present else "target_not_present",
            }
        self.trace.append({"tool": "process", "arguments": {"target_id": target_id}, "result": result})
        return result


TOOL_SCHEMAS = [
    {
        "name": "observe",
        "description": "Return the current environment state.",
        "arguments": {},
    },
    {
        "name": "refresh",
        "description": "Refresh the environment state. The target list may change.",
        "arguments": {},
    },
    {
        "name": "process",
        "description": "Perform the requested final action on a target entity ID.",
        "arguments": {"target_id": "stable entity id, or INVALID_BOUND_ENTITY if a pre-bound entity disappeared"},
    },
]
