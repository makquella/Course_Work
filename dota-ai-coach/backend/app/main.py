"""
main.py — FastAPI application entry point for Dota AI Coach (MVP-1).
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.schemas import GameSituationRequest, RecommendationResponse
from app.rag import retrieve_context
from app.recommender import generate_recommendation
from app.logger import log_recommendation

app = FastAPI(
    title="Dota AI Coach",
    description="MVP-1: rule-based carry coach with local knowledge-base RAG.",
    version="0.1.0",
)


@app.get("/", summary="Health check")
def root():
    """Simple health-check endpoint."""
    return {"status": "ok", "service": "Dota AI Coach", "version": "0.1.0"}


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
    # Build a free-text query for the RAG module
    query = (
        f"{request.hero} {request.role} {request.game_state} "
        f"{request.team_status} minute {request.minute} level {request.level} "
        f"hp {request.hp_percent} gold {request.gold} "
        + " ".join(request.items)
    )

    rag_context = retrieve_context(query, hero=request.hero, game_state=request.game_state)
    recommendation = generate_recommendation(request, rag_context)
    log_path = log_recommendation(request, rag_context, recommendation)

    # Attach the log filename as a response header for easy debugging
    response = JSONResponse(content=recommendation.model_dump())
    response.headers["X-Log-File"] = log_path.name
    return response
