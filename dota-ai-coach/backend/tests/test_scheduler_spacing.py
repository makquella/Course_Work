from __future__ import annotations


def _state(timestamp: int, *, hp: int = 100, game_state: str = "pressure") -> dict:
    return {
        "hero": "Phantom Lancer",
        "role": "carry",
        "minute": timestamp // 60,
        "level": 15,
        "gold": 0,
        "items": ["Power Treads", "Manta Style"],
        "hp_percent": hp,
        "game_state": game_state,
        "team_status": "unknown",
        "event_context": "test replay pressure",
        "extra_context": {
            "source_type": "replay_gsi_like",
            "context_confidence": "high",
            "game_time": timestamp,
            "timestamp_seconds": timestamp,
            "alive": True,
            "mana_percent": 80,
            "last_hits": 80,
            "farm_quality": "low",
            "hp_pressure_state": "healthy" if hp > 65 else "critical",
            "position_zone": "lane_area",
            "position_risk": "medium",
            "missing_signals": ["enemy_positions", "nearby_allies_enemies"],
        },
    }


def _send_demo_state(client, timestamp: int, state: dict) -> dict:
    response = client.post(
        "/demo/replay-state",
        json={
            "timestamp_seconds": timestamp,
            "state": state,
            "simulation_file": "test_spacing.jsonl",
            "speed": 5,
        },
    )
    assert response.status_code == 200
    return response.json()["overlay"]


def test_duplicate_demo_advice_is_suppressed(client):
    first = _send_demo_state(client, 1200, _state(1200))
    second = _send_demo_state(client, 1205, _state(1205))

    assert first["new_advice"] is True
    assert second["new_advice"] is not True
    assert second["advice_count"] == first["advice_count"]


def test_game_time_spacing_blocks_normal_coaching_every_few_seconds(client):
    first = _send_demo_state(client, 1200, _state(1200))
    second = _send_demo_state(client, 1210, _state(1210, game_state="pressure tower"))

    assert first["new_advice"] is True
    assert second["new_advice"] is not True
    assert second["advice_count"] == first["advice_count"]
    assert second.get("suppressed_by_game_time_spacing") or second["status"] in {
        "active_advice",
        "cooldown",
    }


def test_urgent_low_hp_can_interrupt_game_time_spacing(client):
    first = _send_demo_state(client, 1200, _state(1200))
    urgent = _send_demo_state(client, 1211, _state(1211, hp=28, game_state="pressure"))

    assert first["new_advice"] is True
    assert urgent["decision_point"] == "LOW_HP"
    assert urgent["new_advice"] is True
    assert urgent["game_time_gap_since_previous_advice"] == 11.0
