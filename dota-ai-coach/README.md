# Dota AI Coach

A prototype AI coach for **Dota 2 carry players**.

The system accepts a structured description of a game situation, validates it, retrieves relevant context from a local Markdown knowledge base, applies a rule-based fallback recommendation engine, and logs everything to disk.

> **Status: MVP-1** — rule-based fallback only. No LLM, no external APIs, no overlay.

---

## Project Structure

```
dota-ai-coach/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app and route handlers
│   │   ├── schemas.py       # Pydantic request/response models
│   │   ├── recommender.py   # Rule-based fallback recommendation logic
│   │   ├── rag.py           # Keyword-overlap retrieval from knowledge base
│   │   ├── logger.py        # Per-request JSON log writer
│   │   └── config.py        # Paths and constants
│   ├── logs/                # Auto-created; one JSON file per request
│   └── requirements.txt
├── data/
│   ├── knowledge_base/      # Markdown files read by the RAG module
│   │   ├── carry_principles.md
│   │   ├── heroes.md
│   │   └── items.md
│   └── scenarios/           # Sample JSON inputs for manual testing
│       ├── antimage_14min_pressure.json
│       ├── juggernaut_low_hp.json
│       └── luna_farm_or_fight.json
├── docs/
├── frontend/                # Minimal browser UI for POST /recommend
│   ├── index.html
│   ├── styles.css
│   └── script.js
└── README.md
```

---

## Quick Start

### 1. Create a virtual environment

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the development server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.  
Interactive docs (Swagger UI): `http://127.0.0.1:8000/docs`

### 4. Open the frontend

With the backend server still running, open:

```text
http://127.0.0.1:8000/frontend/
```

The page sends JSON to `http://127.0.0.1:8000/recommend` and displays the returned recommendation fields.

---

## Example Request

### Health check

```bash
curl http://127.0.0.1:8000/
```

**Response:**
```json
{"status": "ok", "service": "Dota AI Coach", "version": "0.1.0"}
```

### POST /recommend — Anti-Mage under pressure

```bash
curl -X POST http://127.0.0.1:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "hero": "Anti-Mage",
    "role": "carry",
    "minute": 14,
    "level": 10,
    "gold": 1800,
    "items": ["Power Treads", "Ring of Health", "Claymore"],
    "hp_percent": 70,
    "game_state": "enemy_pressure_mid",
    "team_status": "supports_dead"
  }'
```

**Response:**
```json
{
  "action": "Avoid fights — switch to a safe jungle camp or pull back to base.",
  "reason": "The enemy is applying pressure at minute 14 and you are still in the early-game farming phase. Dying now delays your core items significantly.",
  "risk": "Medium — losing farm and potentially a death if you contest.",
  "priority": "high",
  "time_window": "For the next 3–4 minutes until your supports rotate or respawn.",
  "source": "fallback"
}
```

### POST /recommend — Juggernaut with low HP (uses a scenario file)

```bash
curl -X POST http://127.0.0.1:8000/recommend \
  -H "Content-Type: application/json" \
  -d @../data/scenarios/juggernaut_low_hp.json
```

### POST /recommend — Luna farm or fight decision

```bash
curl -X POST http://127.0.0.1:8000/recommend \
  -H "Content-Type: application/json" \
  -d @../data/scenarios/luna_farm_or_fight.json
```

---

## How it Works

1. **Input validation** — Pydantic checks every field (type, range, allowed values).
2. **RAG retrieval** — All `.md` files in `data/knowledge_base/` are split into paragraphs and the top 3 most keyword-relevant paragraphs for the current situation are extracted.
3. **Fallback recommender** — A short rule chain produces a structured recommendation based on HP level, game-state keywords, and hero level.
4. **Logging** — Every request is saved as a timestamped JSON file in `backend/logs/`.

---

## Roadmap

| Version | Feature |
|---------|---------|
| MVP-1 *(current)* | Rule-based fallback, local keyword RAG, JSON logging |
| MVP-2 | LLM integration (Ollama / OpenAI API) to replace fallback logic |
| MVP-3 | Embedding-based semantic RAG (sentence-transformers or similar) |
| MVP-4 | OpenDota/STRATZ API integration for real match data |
| MVP-5 | In-game overlay via Electron or browser extension |

---

## Requirements

- Python 3.11+
- FastAPI 0.111
- Uvicorn 0.30
- Pydantic 2.7
