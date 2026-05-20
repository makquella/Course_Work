"""
gsi_state.py — in-memory Dota 2 Game State Integration state for MVP overlay use.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


_latest_raw_payload: dict[str, Any] | None = None
_latest_normalized_state: dict[str, Any] | None = None
_latest_timestamp: str | None = None

_HERO_NAME_MAP = {
    "npc_dota_hero_antimage": "Anti-Mage",
    "npc_dota_hero_juggernaut": "Juggernaut",
    "npc_dota_hero_luna": "Luna",
    "antimage": "Anti-Mage",
    "anti-mage": "Anti-Mage",
    "juggernaut": "Juggernaut",
    "luna": "Luna",
}

_ITEM_NAME_MAP = {
    "item_bfury": "Battle Fury",
    "item_power_treads": "Power Treads",
    "item_phase_boots": "Phase Boots",
    "item_ring_of_health": "Ring of Health",
    "item_claymore": "Claymore",
    "item_magic_wand": "Magic Wand",
    "item_manta": "Manta Style",
    "item_maelstrom": "Maelstrom",
    "item_helm_of_the_dominator": "Helm of the Dominator",
    "item_tango": "Tango",
    "item_branches": "Iron Branch",
}

_EMPTY_ITEM_NAMES = {"", "empty", "item_empty", "item_unknown", "item_none"}


def update_latest_gsi(payload: dict[str, Any]) -> dict[str, Any]:
    global _latest_raw_payload, _latest_normalized_state, _latest_timestamp

    _latest_raw_payload = payload
    _latest_normalized_state = normalize_gsi_payload(payload)
    _latest_timestamp = datetime.now(timezone.utc).isoformat()
    return {
        "status": "ok",
        "timestamp": _latest_timestamp,
        "state": _latest_normalized_state,
    }


def get_current_state() -> dict[str, Any]:
    if _latest_normalized_state is None:
        return {
            "status": "waiting_for_gsi",
            "timestamp": None,
            "state": None,
        }

    return {
        "status": "ok",
        "timestamp": _latest_timestamp,
        "state": _latest_normalized_state,
    }


def normalize_gsi_payload(payload: dict[str, Any]) -> dict[str, Any]:
    hero_block = _dict_value(payload.get("hero"))
    player_block = _dict_value(payload.get("player"))
    map_block = _dict_value(payload.get("map"))

    hero = _normalize_hero_name(
        _first_value(
            payload.get("hero_name"),
            payload.get("hero") if isinstance(payload.get("hero"), str) else None,
            hero_block.get("name"),
        )
    )
    if payload.get("minute") is not None:
        minute = _clamp_int(payload.get("minute"), 0, 90, default=0)
    else:
        minute = _normalize_minute(_first_value(map_block.get("clock_time"), map_block.get("game_time")))
    level = _clamp_int(_first_value(payload.get("level"), hero_block.get("level")), 1, 30, default=1)
    gold = _clamp_int(_first_value(payload.get("gold"), player_block.get("gold")), 0, None, default=0)
    hp_percent = _normalize_hp_percent(payload, hero_block)
    game_state = _normalize_game_state(payload, map_block)
    team_status = _normalize_team_status(payload, hero_block)
    items = _normalize_items(payload.get("items"))

    return {
        "hero": hero,
        "role": "carry",
        "minute": minute,
        "level": level,
        "gold": gold,
        "items": items,
        "hp_percent": hp_percent,
        "game_state": game_state,
        "team_status": team_status,
    }


def _dict_value(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _first_value(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None


def _clamp_int(value: Any, minimum: int, maximum: int | None, default: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = default
    number = max(minimum, number)
    if maximum is not None:
        number = min(maximum, number)
    return number


def _normalize_minute(value: Any) -> int:
    try:
        seconds = int(value)
    except (TypeError, ValueError):
        return 0
    if seconds < 0:
        return 0
    return min(seconds // 60, 90)


def _normalize_hp_percent(payload: dict[str, Any], hero_block: dict[str, Any]) -> int:
    direct = _first_value(payload.get("hp_percent"), hero_block.get("health_percent"))
    if direct is not None:
        return _clamp_int(direct, 0, 100, default=100)

    health = hero_block.get("health")
    max_health = hero_block.get("max_health")
    try:
        if int(max_health) > 0:
            return _clamp_int(round((int(health) / int(max_health)) * 100), 0, 100, default=100)
    except (TypeError, ValueError):
        pass
    return 100


def _normalize_hero_name(value: Any) -> str:
    raw_name = str(value or "").strip()
    key = raw_name.lower()
    if key in _HERO_NAME_MAP:
        return _HERO_NAME_MAP[key]
    if key.startswith("npc_dota_hero_"):
        key = key.removeprefix("npc_dota_hero_")
    return _title_from_token(key) if key else "Unknown"


def _normalize_items(value: Any) -> list[str]:
    if isinstance(value, list):
        items: list[str] = []
        for item in value:
            normalized = _normalize_item_name(item)
            if normalized:
                items.append(normalized)
        return items
    if not isinstance(value, dict):
        return []

    items: list[str] = []
    for slot_name in sorted(value):
        slot = value[slot_name]
        item_name = slot.get("name") if isinstance(slot, dict) else slot
        normalized = _normalize_item_name(item_name)
        if normalized:
            items.append(normalized)
    return items


def _normalize_item_name(value: Any) -> str:
    raw_name = str(value or "").strip()
    key = raw_name.lower()
    if key in _EMPTY_ITEM_NAMES:
        return ""
    if key in _ITEM_NAME_MAP:
        return _ITEM_NAME_MAP[key]
    if key.startswith("item_"):
        key = key.removeprefix("item_")
    return _title_from_token(key)


def _normalize_game_state(payload: dict[str, Any], map_block: dict[str, Any]) -> str:
    state = _first_value(
        payload.get("game_state"),
        payload.get("event"),
        map_block.get("name"),
        map_block.get("game_state"),
    )
    return str(state or "gsi_update").strip() or "gsi_update"


def _normalize_team_status(payload: dict[str, Any], hero_block: dict[str, Any]) -> str:
    if payload.get("team_status"):
        return str(payload["team_status"]).strip()
    if hero_block.get("alive") is False:
        return "hero_dead"
    return "unknown"


def _title_from_token(value: str) -> str:
    return value.replace("_", " ").replace("-", " ").title()
