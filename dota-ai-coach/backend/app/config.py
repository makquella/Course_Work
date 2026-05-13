"""
config.py — paths and global settings for the application.
"""

from pathlib import Path

# Root of the repository (app/ -> backend/ -> dota-ai-coach/)
REPO_ROOT = Path(__file__).resolve().parents[2]

# Where Markdown knowledge-base files live
KNOWLEDGE_BASE_DIR = REPO_ROOT / "data" / "knowledge_base"

# Where per-request log files are written
LOGS_DIR = Path(__file__).resolve().parents[1] / "logs"

# How many RAG paragraphs to return
RAG_TOP_K = 3
