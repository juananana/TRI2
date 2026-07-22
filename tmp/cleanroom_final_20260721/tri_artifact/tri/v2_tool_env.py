from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .reference_lifecycle import INVALID


def _exact_match(pred: str | list[str], gold: str | list[str]) -> bool:
    if isinstance(pred, list) or isinstance(gold, list):
        return list(pred) == list(gold) if isinstance(pred, list) and isinstance(gold, list) else False
    return pred == gold


@dataclass
class AppStyleEnvironment:
    """Stateful app-style environment for TRI-v2 tasks."""

    task: dict[str, Any]
    refreshed: bool = False
    acted_target: str | list[str] | None = None
    trace: list[dict[str, Any]] = field(default_factory=list)

    @property
    def current_state(self) -> list[dict[str, Any]]:
        return self.task["refreshed_state"] if self.refreshed else self.task["initial_state"]

    def open_app(self) -> dict[str, Any]:
        result = {
            "ok": True,
            "tool": "open_app",
            "app": self.task["app"],
            "entities": self.current_state,
        }
        self.trace.append({"tool": "open_app", "result": result})
        return result

    def refresh_app(self) -> dict[str, Any]:
        self.refreshed = True
        result = {
            "ok": True,
            "tool": "refresh_app",
            "app": self.task["app"],
            "entities": self.current_state,
        }
        self.trace.append({"tool": "refresh_app", "result": result})
        return result

    def perform_action(self, target: str | list[str]) -> dict[str, Any]:
        self.acted_target = target
        ok = _exact_match(target, self.task["correct_target"])
        result = {
            "ok": ok,
            "tool": "perform_action",
            "action": self.task["action"],
            "target": target,
            "status": "success" if ok else "wrong_target",
        }
        if target == INVALID:
            result["status"] = "invalid_bound_entity" if ok else "invalid_requested_incorrectly"
        self.trace.append({"tool": "perform_action", "arguments": {"target": target}, "result": result})
        return result


TOOL_SCHEMAS = [
    {
        "name": "open_app",
        "description": "Open the named app and return the current app state.",
        "arguments": {"app": "application name"},
    },
    {
        "name": "refresh_app",
        "description": "Refresh the app state. Entities may be reordered, renamed, removed, or invalidated.",
        "arguments": {"app": "application name"},
    },
    {
        "name": "perform_action",
        "description": "Perform the requested user action on an entity id, owner id, list of ids, or INVALID_BOUND_ENTITY.",
        "arguments": {"target": "entity id, owner id, list of ids, or INVALID_BOUND_ENTITY"},
    },
]
