"""ToolSandbox-based custom extension for external TRI validation."""

from .scenarios import (
    Scenario,
    build_pilot_scenarios,
    build_single_turn_2x2_scenarios,
)

__all__ = ["Scenario", "build_pilot_scenarios", "build_single_turn_2x2_scenarios"]
