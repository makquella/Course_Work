"""
decision_points.py — tiny event detector for GSI-driven overlay advice.
"""

from collections.abc import Mapping
from typing import Any, Literal


DecisionPoint = Literal[
    "LOW_HP",
    "FARMING_PHASE_PRESSURE",
    "OBJECTIVE_FIGHT_CHECK",
    "NO_ADVICE",
]

PRESSURE_KEYWORDS = {
    "pressure",
    "gank",
    "ganked",
    "danger",
    "smoke",
    "enemy_push",
    "tower_pressure",
    "under_attack",
}

OBJECTIVE_FIGHT_KEYWORDS = {
    "fight",
    "teamfight",
    "objective",
    "roshan",
    "tower",
    "barracks",
    "push",
    "contest",
}


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _state_text(state: Mapping[str, Any]) -> str:
    return " ".join(
        str(state.get(key, ""))
        for key in ("game_state", "team_status")
    ).lower()


def has_pressure_signal(state: Mapping[str, Any]) -> bool:
    text = _state_text(state)
    return any(keyword in text for keyword in PRESSURE_KEYWORDS)


def has_objective_fight_signal(state: Mapping[str, Any]) -> bool:
    text = _state_text(state)
    return any(keyword in text for keyword in OBJECTIVE_FIGHT_KEYWORDS)


def detect_decision_point(state: Mapping[str, Any] | None) -> DecisionPoint:
    if not state:
        return "NO_ADVICE"

    hp_percent = _to_int(state.get("hp_percent"), default=100)
    minute = _to_int(state.get("minute"), default=0)

    if hp_percent <= 35:
        return "LOW_HP"

    if minute < 18 and has_pressure_signal(state):
        return "FARMING_PHASE_PRESSURE"

    if has_objective_fight_signal(state):
        return "OBJECTIVE_FIGHT_CHECK"

    return "NO_ADVICE"
