"""
recommender.py — rule-based fallback recommendation logic for MVP-1.

Rules are evaluated top-to-bottom; the first matching rule wins.
"""

from app.schemas import GameSituationRequest, RecommendationResponse


def generate_recommendation(req: GameSituationRequest) -> RecommendationResponse:
    """Apply simple priority rules and return a structured recommendation."""

    # Rule 1 — critically low HP: survive first.
    if req.hp_percent <= 35:
        return RecommendationResponse(
            action="Retreat immediately — move to safety or recall to base.",
            reason=(
                f"Your HP is at {req.hp_percent}%, which is below the safe threshold. "
                "Fighting at this HP level risks a free kill for the enemy."
            ),
            risk="High risk of dying if you stay in the lane or jungle.",
            priority="high",
            time_window="Immediate — act within the next 10–15 seconds.",
        )

    # Rule 2 — enemy pressure early game: avoid low-value fights.
    if "pressure" in req.game_state.lower() and req.minute < 18:
        return RecommendationResponse(
            action="Avoid fights — switch to a safe jungle camp or pull back to base.",
            reason=(
                f"The enemy is applying pressure at minute {req.minute} and you are still "
                "in the early-game farming phase. Dying now delays your core items significantly."
            ),
            risk="Medium — losing farm and potentially a death if you contest.",
            priority="high",
            time_window="For the next 3–4 minutes until your supports rotate or respawn.",
        )

    # Rule 3 — fight scenario with sufficient level: join only near objectives.
    if "fight" in req.game_state.lower() and req.level >= 12:
        return RecommendationResponse(
            action="Join the fight only if it is near Roshan, Barracks, or a tower.",
            reason=(
                f"At level {req.level} you have enough fighting capability, but trading "
                "fights away from objectives gives you no structural advantage."
            ),
            risk="Medium — joining random fights without objective payoff wastes your power spike.",
            priority="medium",
            time_window="Decide within 20–30 seconds; the fight window is short.",
        )

    # Default — focus on farming and objective timing.
    return RecommendationResponse(
        action="Focus on efficient farming and track the next major objective timing.",
        reason=(
            f"At minute {req.minute} with {req.gold} gold, maximising your farm rate is "
            "the highest-value action. Keep an eye on Roshan and tower timings."
        ),
        risk="Low — avoid unnecessary risks while ahead on farm.",
        priority="low",
        time_window="Ongoing; reassess every 2–3 minutes.",
    )
