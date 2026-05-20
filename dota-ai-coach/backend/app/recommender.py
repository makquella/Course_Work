"""
recommender.py — rule-based fallback recommendation logic for MVP-1.

Rules are evaluated top-to-bottom; the first matching rule wins.
RAG context is used to find a specific timing/weakness hint for the reason field,
not to paste raw paragraphs.
"""

from app.schemas import GameSituationRequest, RecommendationResponse
from app.decision_points import has_objective_fight_signal, has_pressure_signal


def _find_timing_hint(rag_context: list[str]) -> str:
    """
    Scan RAG paragraphs for a sentence about hero weakness or item power spike.
    Returns the first matching sentence, or an empty string.
    """
    spike_keywords = {"spike", "weak", "until"}
    for para in rag_context:
        for sentence in para.replace("\n", " ").split("."):
            s = sentence.strip()
            if len(s) < 20 or s.startswith("#"):
                continue
            if any(kw in s.lower() for kw in spike_keywords):
                return s + "."
    return ""


def generate_recommendation(
    req: GameSituationRequest,
    rag_context: list[str],
) -> RecommendationResponse:
    """Apply simple priority rules and return a structured recommendation."""

    # Rule 1 — critically low HP: survive first.
    # RAG hint skipped — low HP reasoning is self-explanatory and must not contradict retreat.
    if req.hp_percent <= 35:
        return RecommendationResponse(
            action="Retreat immediately — move to safety or recall to base.",
            reason=(
                f"At {req.hp_percent}% HP you are a free kill for any initiator. "
                "Retreat now and recover before rejoining the fight."
            ),
            risk="High risk of dying if you stay in the lane or jungle.",
            priority="high",
            time_window="immediate: next 10-15 seconds",
        )

    # Rule 2 — enemy pressure early game: avoid low-value fights.
    # RAG hint: look for hero-specific weakness or item timing info.
    state = {"game_state": req.game_state, "team_status": req.team_status}

    if has_pressure_signal(state) and req.minute < 18:
        hint = _find_timing_hint(rag_context)
        reason = (
            f"{req.hero} is in the early farming phase at minute {req.minute} "
            "and should not contest enemy pressure without item advantage."
        )
        if hint:
            reason += f" {hint}"
        return RecommendationResponse(
            action="Avoid fights — switch to a safe jungle camp or pull back to base.",
            reason=reason,
            risk="Medium — losing farm and potentially a death if you contest.",
            priority="high",
            time_window="next 60-90 seconds",
        )

    # Rule 3 — fight scenario with sufficient level: join only near objectives.
    # RAG hint skipped — adding a "farm more" hint here would contradict the fight advice.
    if has_objective_fight_signal(state) and req.level >= 12:
        return RecommendationResponse(
            action="Join the fight only if it is near Roshan, Barracks, or a tower.",
            reason=(
                f"At level {req.level} you can contribute to a fight, but only near "
                "a valuable objective. Random skirmishes away from structures delay "
                "your item timing without strategic payoff."
            ),
            risk="Medium — joining random fights without objective payoff wastes your power spike.",
            priority="medium",
            time_window="next 60-90 seconds",
        )

    # Default — focus on farming and objective timing.
    hint = _find_timing_hint(rag_context)
    reason = (
        f"At minute {req.minute} with {req.gold} gold, maximising farm rate is "
        "the highest-value action."
    )
    if hint:
        reason += f" {hint}"
    return RecommendationResponse(
        action="Focus on efficient farming and track the next major objective timing.",
        reason=reason,
        risk="Low — avoid unnecessary risks while maintaining farm efficiency.",
        priority="low",
        time_window="reassess in 60 seconds",
    )
