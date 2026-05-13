"""
rag.py — simple keyword-based retrieval from local Markdown knowledge base.

No embeddings — just paragraph splitting and token-overlap scoring.
"""

from pathlib import Path
from app.config import KNOWLEDGE_BASE_DIR, RAG_TOP_K


def _load_paragraphs(kb_dir: Path) -> list[str]:
    """Read all .md files and split into non-empty paragraphs."""
    paragraphs: list[str] = []
    for md_file in sorted(kb_dir.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        for para in text.split("\n\n"):
            stripped = para.strip()
            if stripped:
                paragraphs.append(stripped)
    return paragraphs


def _score(paragraph: str, query_tokens: set[str]) -> int:
    """Count how many query tokens appear in the paragraph (case-insensitive)."""
    para_tokens = set(paragraph.lower().split())
    return len(query_tokens & para_tokens)


def retrieve_context(query: str, top_k: int = RAG_TOP_K) -> list[str]:
    """
    Return the top_k most relevant paragraphs from the knowledge base
    for the given query string.
    """
    paragraphs = _load_paragraphs(KNOWLEDGE_BASE_DIR)
    if not paragraphs:
        return []

    query_tokens = set(query.lower().split())
    scored = [(para, _score(para, query_tokens)) for para in paragraphs]
    # Sort by score descending; keep only paragraphs with at least one match
    scored.sort(key=lambda x: x[1], reverse=True)
    top = [para for para, score in scored[:top_k] if score > 0]
    return top
