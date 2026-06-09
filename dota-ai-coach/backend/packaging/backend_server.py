"""
Packaged backend entry point for Dota AI Coach.

This module is intentionally small: it starts the existing FastAPI app without
changing recommendation, scheduler, parser, GSI, or overlay behavior.
"""

from __future__ import annotations

import os

import uvicorn


def main() -> int:
    os.environ.setdefault("USE_LLM", "false")
    os.environ.setdefault("SIMULATION_USE_LLM", "false")

    uvicorn.run(
        "app.main:app",
        host=os.environ.get("DOTA_AI_BACKEND_HOST", "127.0.0.1"),
        port=int(os.environ.get("DOTA_AI_BACKEND_PORT", "8000")),
        access_log=False,
        log_level=os.environ.get("DOTA_AI_BACKEND_LOG_LEVEL", "info"),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
