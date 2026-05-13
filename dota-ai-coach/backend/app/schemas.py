"""
schemas.py — Pydantic models for request and response validation.
"""

from typing import Literal
from pydantic import BaseModel, Field


class GameSituationRequest(BaseModel):
    hero: str = Field(..., min_length=1, description="Hero name, e.g. 'Anti-Mage'")
    role: Literal["carry"] = Field(..., description="Only 'carry' is supported in MVP-1")
    minute: int = Field(..., ge=0, le=90, description="Current game minute (0–90)")
    level: int = Field(..., ge=1, le=30, description="Hero level (1–30)")
    gold: int = Field(..., ge=0, description="Current gold amount")
    items: list[str] = Field(..., description="List of item names the hero currently owns")
    hp_percent: int = Field(..., ge=0, le=100, description="Current HP as a percentage (0–100)")
    game_state: str = Field(..., min_length=1, description="Short description of the current game state")
    team_status: str = Field(..., min_length=1, description="Short description of teammate situation")


class RecommendationResponse(BaseModel):
    action: str
    reason: str
    risk: str
    priority: Literal["low", "medium", "high"]
    time_window: str
    source: Literal["fallback"] = "fallback"
