"""
main.py — FastAPI application entry point for Dota AI Coach (MVP-1).
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from app.decision_points import detect_decision_point
from app.gsi_state import get_current_state, update_latest_gsi
from app.schemas import GameSituationRequest, RecommendationResponse
from app.rag import retrieve_context
from app.recommender import generate_recommendation
from app.logger import log_recommendation

app = FastAPI(
    title="Dota AI Coach",
    description="MVP-1: rule-based carry coach with local knowledge-base RAG.",
    version="0.1.0",
)

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
OVERLAY_COOLDOWN_SECONDS = 60
COOLDOWN_BYPASS_EVENTS = {"LOW_HP"}

_last_overlay_recommendation: dict[str, Any] | None = None
_last_overlay_generated_at: datetime | None = None
_last_overlay_event: str | None = None

if FRONTEND_DIR.exists():
    app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


@app.get("/", summary="Health check")
def root():
    """Simple health-check endpoint."""
    return {"status": "ok", "service": "Dota AI Coach", "version": "0.1.0"}


def _build_recommendation(request: GameSituationRequest) -> tuple[RecommendationResponse, str]:
    # Build a free-text query for the RAG module
    query = (
        f"{request.hero} {request.role} {request.game_state} "
        f"{request.team_status} minute {request.minute} level {request.level} "
        f"hp {request.hp_percent} gold {request.gold} "
        + " ".join(request.items)
    )

    rag_context = retrieve_context(
        query,
        hero=request.hero,
        game_state=request.game_state,
        owned_items=request.items,
    )
    recommendation = generate_recommendation(request, rag_context)
    log_path = log_recommendation(request, rag_context, recommendation)
    return recommendation, log_path.name


@app.post("/recommend", response_model=RecommendationResponse, summary="Get a carry recommendation")
def recommend(request: GameSituationRequest):
    """
    Accept a structured game-situation description and return a carry recommendation.

    Steps:
    1. Build a query string from the request for RAG retrieval.
    2. Retrieve relevant knowledge-base paragraphs.
    3. Generate a rule-based fallback recommendation.
    4. Log the full request/context/response to disk.
    5. Return the recommendation.
    """
    recommendation, log_filename = _build_recommendation(request)
    # Attach the log filename as a response header for easy debugging
    response = JSONResponse(content=recommendation.model_dump())
    response.headers["X-Log-File"] = log_filename
    return response


@app.post("/gsi", summary="Receive Dota 2 Game State Integration data")
async def receive_gsi(request: Request):
    """Accept raw Dota 2 GSI JSON and keep the latest normalized state in memory."""
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "detail": "Request body must be valid JSON."},
        )

    if not isinstance(payload, dict):
        return JSONResponse(
            status_code=400,
            content={"status": "error", "detail": "GSI payload must be a JSON object."},
        )

    return update_latest_gsi(payload)


@app.get("/state/current", summary="Get latest normalized GSI state")
def current_state():
    return get_current_state()


@app.get("/overlay/recommendation", summary="Get overlay-friendly recommendation")
def overlay_recommendation():
    global _last_overlay_event, _last_overlay_generated_at, _last_overlay_recommendation

    current = get_current_state()
    if current["status"] == "waiting_for_gsi":
        return {
            "status": "waiting_for_gsi",
            "timestamp": None,
            "event": "NO_ADVICE",
            "recommendation": None,
        }

    state = current["state"] or {}
    event = detect_decision_point(state)

    if event == "NO_ADVICE":
        return {
            "status": "no_advice",
            "timestamp": current["timestamp"],
            "event": event,
            "recommendation": None,
        }

    now = datetime.now(timezone.utc)
    cooldown_remaining = _cooldown_remaining(now)
    if cooldown_remaining > 0 and event not in COOLDOWN_BYPASS_EVENTS:
        return {
            "status": "cooldown",
            "timestamp": current["timestamp"],
            "event": event,
            "recommendation": _last_overlay_recommendation if event == _last_overlay_event else None,
            "cooldown_remaining_seconds": cooldown_remaining,
        }

    try:
        request = GameSituationRequest(**state)
    except ValidationError as exc:
        return {
            "status": "invalid_state",
            "timestamp": current["timestamp"],
            "event": event,
            "recommendation": None,
            "detail": exc.errors(include_context=False),
        }

    recommendation, log_filename = _build_recommendation(request)
    _last_overlay_recommendation = recommendation.model_dump()
    _last_overlay_generated_at = now
    _last_overlay_event = event

    return {
        "status": "ok",
        "timestamp": current["timestamp"],
        "event": event,
        "recommendation": _last_overlay_recommendation,
        "cooldown_remaining_seconds": OVERLAY_COOLDOWN_SECONDS,
        "log_file": log_filename,
    }


def _cooldown_remaining(now: datetime) -> int:
    if _last_overlay_generated_at is None:
        return 0
    elapsed = (now - _last_overlay_generated_at).total_seconds()
    return max(0, int(OVERLAY_COOLDOWN_SECONDS - elapsed))
