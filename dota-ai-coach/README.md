# Dota AI Coach

A coursework prototype AI coach for **Dota 2 carry players**.

The system receives live Dota 2 Game State Integration (GSI) updates or offline GSI-like replay states, normalizes them, applies deterministic rule-based carry coaching, schedules advice through an anti-spam layer, and shows compact advice in a desktop overlay. Optional LLM providers can improve wording during offline evaluation or controlled demos, but local rule-based policy remains authoritative for live decisions.

> **Status: coursework MVP** — FastAPI backend, live GSI endpoint, deterministic realtime recommender, game-time based scheduler, Electron desktop overlay, launcher UI, replay parser/converter, replay demo playback, live session recorder, simulation/evaluation scripts, and Windows packaging Phase 1. The project does not read game memory, does not read the screen, does not automate input, does not inject into Dota 2, and does not use STRATZ or a database.

---

## Project Structure

```
dota-ai-coach/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app, GSI/demo/overlay endpoints
│   │   ├── gsi_state.py            # Live GSI normalization
│   │   ├── recommender.py          # Rule-based fallback wording
│   │   ├── advice_scheduler.py     # Anti-spam, game-time spacing, active cards
│   │   ├── advice_policy.py        # Local priority/time-window policy
│   │   ├── advice_context.py       # Farm, HP, and position context
│   │   ├── advice_text.py          # Advice wording templates
│   │   ├── advice_ux_policy.py     # UX guard for advice display
│   │   ├── coach_summary.py        # Post-session coaching summary builder
│   │   ├── decision_points.py      # Decision point detection logic
│   │   ├── laning_coach.py         # Laning Coach v1
│   │   ├── post_laning_coach.py    # Post-Laning Farming Coach v1
│   │   ├── item_timing.py          # Meaningful item timing helpers
│   │   ├── hero_profiles.py        # Data-driven hero profile loader
│   │   ├── hero_safety.py          # Hero survivability checks
│   │   ├── signal_capabilities.py  # Source-specific signal availability
│   │   ├── match_memory.py         # In-memory live match/death memory
│   │   ├── live_session_recorder.py # Local GSI session recorder
│   │   ├── deep_replay_review.py   # Offline replay review artifact builder
│   │   ├── llm_provider.py         # Optional Groq/llama.cpp/OpenRouter calls
│   │   ├── schemas.py              # Pydantic request/response models
│   │   ├── rag.py                  # Keyword-overlap knowledge retrieval
│   │   ├── logger.py               # Per-request JSON log writer
│   │   └── config.py               # Paths and settings
│   ├── scripts/                    # Simulation, replay, demo, comparison tools
│   ├── tests/                      # pytest API/GSI/scheduler/recorder tests
│   ├── replay_tools/clarity/       # Offline Clarity helper project
│   ├── packaging/                  # PyInstaller Phase 1 backend specs
│   ├── logs/                       # Auto-created; local request logs
│   └── requirements.txt
├── data/
│   ├── gsi_samples/                # Representative live-style GSI payloads
│   ├── heroes/                     # hero_profiles.json, hero_safety_rules.json
│   ├── match_simulations/          # selected replay/demo JSONL inputs
│   ├── meta/                       # local metadata files
│   ├── opendota/                   # Cached OpenDota match JSON responses
│   ├── replays/                    # Downloaded .dem replay files
│   ├── scenarios/                  # legacy recommend endpoint examples
│   └── knowledge_base/             # Markdown files read by RAG
├── docs/
│   ├── ADVICE_SCHEDULER.md
│   └── PACKAGING_WINDOWS.md
├── frontend/
│   ├── index.html / overlay.html   # legacy simple debug/fallback frontend
│   ├── desktop-overlay/            # Electron always-on-top overlay
│   └── launcher/                   # Electron launcher for defense/demo
├── scripts/                        # project-level demo shell helpers
├── AUTHORS.md
├── LICENSE
└── README.md
```

---

## Project status and safety limits

- Realtime advice is rule-based and deterministic.
- LLM is optional and is not required for live decisions.
- The local policy controls `priority` and `time_window`; LLM wording cannot override those fields.
- Live mode only reads local HTTP GSI updates from Dota 2.
- Backend CORS is local-only for `localhost` / `127.0.0.1` development and packaged launcher/overlay access.
- The system does not read memory, does not read the screen, does not automate input, and does not inject into Dota 2.
- Live GSI provides limited signals. Exact enemy positions, nearby ally/enemy counts, exact teamfight context, exact team readiness, and exact Roshan/objective context are unavailable unless explicitly present in the input.
- Offline replay-derived advice is conservative because the minimal Clarity helper cannot reconstruct every live GSI signal.
- This is a prototype/MVP for coursework defense, not a production coaching product.

## Testing

Run the backend test suite and compile checks:

```bash
cd backend
source .venv/bin/activate
pytest -q
python3 -m compileall -q app scripts packaging tests
```

Optional explicit test path:

```bash
pytest -q backend/tests
```

From the project root, also run:

```bash
git diff --check
node --check frontend/launcher/main.js
node --check frontend/launcher/preload.js
node --check frontend/launcher/renderer/app.js
node --check frontend/desktop-overlay/main.js
node --check frontend/desktop-overlay/preload.js
node --check frontend/desktop-overlay/renderer/app.js
```

## How this project was tested

- Unit/API tests with `pytest` and FastAPI `TestClient`.
- GSI sample parsing tests for representative live payloads.
- Advice behavior tests for low HP, low farm, duplicate suppression, game-time spacing, and urgent LOW_HP interrupts.
- Replay-derived JSONL sanity tests for launcher demo files.
- Live session recorder tests using `tmp_path`.
- Offline replay simulations and review exports.
- Manual launcher/desktop overlay tests for defense demo playback.
- Planned real Dota live test via GSI recording.

## Authorship and license

- Author: Artem / makquella
- Project: Dota AI Coach coursework prototype
- Year: 2026
- License: MIT, see [LICENSE](LICENSE).

Dota 2 is a trademark/game by Valve. This project is an educational prototype and is not affiliated with Valve.

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
Use a preset scenario button or edit the JSON manually, then click **Get Recommendation**.

### Optional: enable runtime LLM recommendations

The fallback recommender works without any API key and remains required for safety. To try an optional LLM provider, create a local env file:

```bash
cp backend/.env.example backend/.env
```

Recommended live Groq setup:

```text
USE_LLM=true
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
LLM_TIMEOUT=6
LLM_MAX_TOKENS=350
```

Groq `openai/gpt-oss-120b` is the recommended live candidate from the offline benchmark flow. OpenRouter is still supported, but the free OpenRouter model path was unstable during testing and should be treated as a fallback experiment:

```text
USE_LLM=true
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openai/gpt-oss-120b:free
LLM_TIMEOUT=6
LLM_MAX_TOKENS=350
```

### Local llama.cpp provider

You can also test a local OpenAI-compatible llama.cpp server. This is optional and is not the default live provider.

Start `llama-server` with your local GGUF model, for example:

```bash
llama-server -m /path/to/model.gguf --host 127.0.0.1 --port 8080
```

Then configure the backend:

```text
USE_LLM=true
LLM_PROVIDER=llamacpp
LLAMACPP_BASE_URL=http://127.0.0.1:8080
LLAMACPP_MODEL=local-gpt-oss-20b
LLM_TIMEOUT=6
LLM_MAX_TOKENS=250
```

No API key is required for llama.cpp. If the local server is not running, times out, returns invalid JSON, or misses required fields, the backend uses the rule-based fallback.

Use `LLM_PROVIDER=disabled` or `USE_LLM=false` to disable runtime LLM calls. `backend/.env` is ignored by git, so API keys stay local. Do not commit API keys or paste them into source files. Then restart the backend:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

Defaults:

- `USE_LLM=false`
- `LLM_PROVIDER=disabled`
- `LLM_TIMEOUT=6`
- `LLM_MAX_TOKENS=350`
- `GROQ_MODEL=openai/gpt-oss-120b`
- `OPENROUTER_MODEL=openai/gpt-oss-120b:free`
- `LLAMACPP_BASE_URL=http://127.0.0.1:8080`
- `LLAMACPP_MODEL=local-gpt-oss-20b`

LLM behavior is conservative and optional:

- LLM is called only after a valid decision point is detected.
- `NO_ADVICE` overlay states do not call the LLM.
- If an API key is missing, the local server is unavailable, the request times out, the provider fails, or invalid JSON is returned, the backend uses the existing fallback recommender.
- The public recommendation response keeps the same fields: `action`, `reason`, `risk`, `priority`, `time_window`, and `source`.

### Universal Carry Advice Policy

The current MVP focuses on safe, abstract carry decisions instead of hero-specific item builds or patch meta. The local policy controls priority and time window, so LLM output cannot make advice more urgent or change timing on its own.

The policy prefers:

- avoid deaths;
- avoid low-value fights;
- farm safely under pressure;
- join fights only around objectives;
- reassess regularly.

Dynamic item builds, patch meta updates, OpenDota, and STRATZ are future work.

### Overload prevention and coaching tone

The overlay includes a cognitive load guard so it stays useful during play instead of becoming an autopilot:

- advice is capped at 1-2 hints per minute;
- duplicate hints are suppressed;
- regular advice uses coaching tone such as `Consider...`, `It is safer to...`, or `Prioritize...`;
- urgent warnings like `LOW_HP` stay direct;
- the overlay shows one main action, a short reason, and keeps risk secondary.

The assistant avoids autopilot-like commands such as exact movement, buying, or TP instructions. It gives a small carry decision hint, then lets the player execute.

### Offline LLM model benchmark

You can compare candidate OpenRouter, Groq, or local llama.cpp models offline without changing live `/recommend` or overlay behavior:

```bash
cd backend
python scripts/benchmark_llm_models.py
```

The script loads provider settings from `backend/.env` or the environment, calls each benchmark model once per prepared scenario, prints a table, and saves JSON/CSV results under `backend/benchmark_results/`. The default provider is OpenRouter. Use `OPENROUTER_API_KEY` for OpenRouter or `GROQ_API_KEY` for Groq. Local llama.cpp uses `LLAMACPP_BASE_URL` and `LLAMACPP_MODEL` and does not require an API key. Set `BENCHMARK_PROVIDER`, `BENCHMARK_MODELS`, `BENCHMARK_TIMEOUT`, `BENCHMARK_MAX_TOKENS`, and `BENCHMARK_DELAY_SECONDS` to customize a run.

OpenRouter example with one model:

```bash
cd backend
BENCHMARK_MODELS=openai/gpt-oss-120b:free BENCHMARK_TIMEOUT=20 python scripts/benchmark_llm_models.py
```

Groq example:

```bash
cd backend
BENCHMARK_PROVIDER=groq \
BENCHMARK_MODELS=openai/gpt-oss-120b,llama-3.3-70b-versatile,openai/gpt-oss-20b \
BENCHMARK_TIMEOUT=20 \
BENCHMARK_MAX_TOKENS=350 \
python scripts/benchmark_llm_models.py
```

llama.cpp example:

```bash
cd backend
BENCHMARK_PROVIDER=llamacpp \
LLAMACPP_BASE_URL=http://127.0.0.1:8080 \
BENCHMARK_MODELS=local-gpt-oss-20b \
BENCHMARK_TIMEOUT=20 \
BENCHMARK_MAX_TOKENS=250 \
python scripts/benchmark_llm_models.py
```

### 5. Open the overlay page

With the backend server still running, open:

```text
http://127.0.0.1:8000/frontend/overlay.html
```

The overlay polls `GET /overlay/recommendation` every 5 seconds. It shows `Waiting for Dota 2 GSI...` until `POST /gsi` receives data.

### Desktop overlay mode

For an actual always-on-top desktop overlay window, use the Electron app in `frontend/desktop-overlay/`. It keeps the browser `frontend/overlay.html` as a debug/fallback view, but gives you a transparent frameless desktop window that reads only from the local backend API.

```bash
cd frontend/desktop-overlay
npm install
npm run dev
```

See `frontend/desktop-overlay/README.md` for Dota display settings, hotkeys, click-through mode, and config.

### Launcher / Windows .exe plan

For coursework defense, you can use the lightweight Electron launcher in `frontend/launcher/`. It starts the backend, starts the desktop overlay, installs/checks the Dota GSI config, runs replay demo playback, and shows compact logs.

Run the launcher in dev mode:

```bash
cd ~/Study/CourseWork/dota-ai-coach/frontend/launcher
npm install
npm run dev
```

Launcher buttons:

- `Start Backend` runs the local FastAPI backend with `USE_LLM=false`.
- `Start Overlay` runs the existing Electron overlay from `frontend/desktop-overlay`.
- `Install / Check Dota GSI` writes `gamestate_integration_dota_ai_coach.cfg` pointing to `http://127.0.0.1:8000/gsi`.
- `Run Demo Replay` runs the Phantom Lancer 20-30 replay demo at `speed 5`.
- `Clean logs` hides repeated overlay/demo HTTP polling lines for defense; `Verbose logs` shows the full debug stream.
- Advanced presets include Phantom Lancer 20-30 macro, Juggernaut 10-20 safety, Deep Replay Review export, `simulation_results`, and README shortcuts.

Default GSI config locations checked by the launcher:

```text
C:\Program Files (x86)\Steam\steamapps\common\dota 2 beta\game\dota\cfg\gamestate_integration
C:\Program Files\Steam\steamapps\common\dota 2 beta\game\dota\cfg\gamestate_integration
~/.steam/steam/steamapps/common/dota 2 beta/game/dota/cfg/gamestate_integration
~/.local/share/Steam/steamapps/common/dota 2 beta/game/dota/cfg/gamestate_integration
```

If Dota is installed elsewhere, paste or choose the `gamestate_integration` folder in the launcher.

Future Windows packaging plan:

- build the backend into a local executable with PyInstaller;
- package the launcher with `electron-builder` or `electron-forge`;
- include overlay resources and the backend executable in the launcher installer;
- keep replay demo files and GSI config helper as bundled resources.

### Windows portable packaging

Phase 1 Windows packaging is documented in [docs/PACKAGING_WINDOWS.md](docs/PACKAGING_WINDOWS.md). Build order:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pip install pyinstaller
pyinstaller packaging\dota_ai_coach_backend.spec

cd ..\frontend\desktop-overlay
npm install
npm run pack

cd ..\launcher
npm install
npm run dist
```

Expected launcher output:

```text
frontend\launcher\dist\Dota AI Coach Launcher-0.1.0-portable.exe
```

### Coursework defense demo

You can demonstrate the desktop overlay without launching Dota 2 by replaying existing offline `GSI-like replay states` into the backend. This mode is explicitly a demo replay path: it does not read the screen, read memory, automate input, or inject into Dota. The overlay still receives advice from the real backend decision/scheduler/recommender path.

Use fallback-only mode for a stable defense demo:

Terminal A - start backend:

```bash
cd ~/Study/CourseWork/dota-ai-coach/backend
source .venv/bin/activate
USE_LLM=false uvicorn app.main:app --reload --no-access-log
```

Terminal B - start desktop overlay:

```bash
cd ~/Study/CourseWork/dota-ai-coach/frontend/desktop-overlay
npm install
npm run dev
```

Terminal C - replay the recommended macro/farming demo. Use `--speed 5` for a live coursework defense; `--speed 10` is better for a quick pre-demo smoke test. Demo speed only changes wall-clock playback; advice spacing is based on simulated Dota game time. In real live GSI mode there is no speed-up, so advice appears according to real game time.

```bash
cd ~/Study/CourseWork/dota-ai-coach/backend
source .venv/bin/activate
SIMULATION_USE_LLM=false \
python3 scripts/run_overlay_demo.py \
  --simulation-file ../data/match_simulations/replay_gsi_like_match_8843382732_pl_20_30.jsonl \
  --speed 5 \
  --advice-hold-seconds 8
```

Shortcut for the same Phantom Lancer 20-30 demo:

```bash
cd ~/Study/CourseWork/dota-ai-coach
./scripts/demo_overlay_pl_20_30.sh
```

Alternative noisy post-laning safety scenario:

```bash
cd ~/Study/CourseWork/dota-ai-coach/backend
source .venv/bin/activate
SIMULATION_USE_LLM=false \
python3 scripts/run_overlay_demo.py \
  --simulation-file ../data/match_simulations/replay_gsi_like_match_8843471434_jugg_10_20.jsonl \
  --speed 5 \
  --advice-hold-seconds 8
```

During playback, the overlay should show:

- connection/status line;
- `DEMO REPLAY MODE` label;
- hero and simulated game time;
- stage such as `laning`, `post-laning`, or `macro`;
- one compact advice action and reason;
- priority, source (`fallback` or `llm`), confidence, HP, mana, last hits, and missing-signal count.

Optional LLM wording demo:

```bash
USE_LLM=true \
LLM_PROVIDER=llamacpp \
LLAMACPP_BASE_URL=http://127.0.0.1:8080 \
LLAMACPP_MODEL=local-gpt-oss-20b \
LLM_TIMEOUT=6 \
LLM_MAX_TOKENS=700 \
uvicorn app.main:app --reload
```

The coursework demo should prefer `USE_LLM=false` unless the local LLM server is already running and stable.

### Coach Session Summary demo

After a replay demo, you can export a short post-session coaching summary based only on advice cards that the backend actually showed:

```bash
cd ~/Study/CourseWork/dota-ai-coach/backend
source .venv/bin/activate
SIMULATION_USE_LLM=false \
python3 scripts/run_overlay_demo.py \
  --simulation-file ../data/match_simulations/replay_gsi_like_match_8843382732_pl_20_30.jsonl \
  --speed 5 \
  --advice-hold-seconds 8 \
  --export-summary simulation_results/demo_session_summary_pl_20_30.md \
  --export-summary-json simulation_results/demo_session_summary_pl_20_30.json
```

The summary contains session overview, main detected patterns, key advice moments, focus points, and data limitations. It does not add unavailable facts such as exact enemy positions, team readiness, exact Roshan/objective state, missing cooldowns, or spendable gold when those signals are absent.

### Deep Replay Review demo

For the coursework defense, the richer post-session artifact is **Deep Replay Review v0**. It uses the replay states processed during playback plus the backend advice cards that were actually shown. It remains deterministic/rule-based by default and does not add unavailable information.

```bash
cd ~/Study/CourseWork/dota-ai-coach/backend
source .venv/bin/activate
SIMULATION_USE_LLM=false \
python3 scripts/run_overlay_demo.py \
  --simulation-file ../data/match_simulations/replay_gsi_like_match_8843382732_pl_20_30.jsonl \
  --speed 5 \
  --advice-hold-seconds 8 \
  --export-deep-review simulation_results/deep_review_pl_20_30.md \
  --export-deep-review-json simulation_results/deep_review_pl_20_30.json
```

The Markdown review includes overview, main patterns, key advice moments, farm review, HP/death review, objective review, item timing review, focus points for the next game, and data limitations.

### Real Dota Live Test Checklist

Safety note: Dota AI Coach does not read memory, does not read the screen, does not automate input, and does not inject into Dota 2. Live mode only uses Dota Game State Integration (GSI) updates posted to the local backend. Replay demos use replay-derived GSI-like states.

Use bot lobby, demo hero, or unranked testing first. Keep `LIVE_CONSERVATIVE_MODE=true` for real live tests.

1. Start the launcher:

```bash
cd ~/Study/CourseWork/dota-ai-coach/frontend/launcher
npm install
npm run dev
```

2. Click `Start Backend`.
3. Click `Install / Check Dota GSI`.
4. Click `Start Overlay`.
5. Launch Dota 2 and enter a bot lobby, demo hero, or other safe test environment.
6. In the launcher, click `Check Live GSI`.
7. Confirm the Live GSI panel shows `GSI: connected`, hero, game time, and stage.
8. Click `Start Live Recording`.
9. Verify the overlay shows `LIVE GSI MODE` and advice/status cards.
10. After the test, click `Stop Live Recording`.
11. Click `Open session_records folder` and review the saved JSONL/metadata files.

Live status endpoint:

```bash
curl http://127.0.0.1:8000/gsi/status
```

Live recording endpoints:

```bash
curl -X POST http://127.0.0.1:8000/session-recording/start
curl -X POST http://127.0.0.1:8000/session-recording/stop
curl http://127.0.0.1:8000/session-recording/status
```

Live recording output is stored under `backend/session_records/` by default. Each session contains:

- `raw_gsi_states.jsonl`
- `shown_advice.jsonl`
- `metadata.json`

Troubleshooting:

- `GSI not connected`: reinstall/check the GSI config, restart the Dota lobby, and verify the endpoint is `http://127.0.0.1:8000/gsi`.
- `Overlay not visible`: start backend first, then overlay; use `Ctrl+Shift+H` to show/hide the overlay.
- `Overlay blocking clicks`: live default is click-through/locked. Use `Ctrl+Alt+L` to toggle lock/click-through if needed.
- `Backend port busy`: stop the old backend process or free port `8000`.
- `Stale advice`: if no GSI arrives for more than 5 seconds, the overlay clears old advice and shows `Waiting for GSI...`.
- `Need more logs`: switch launcher from `Clean logs` to `Verbose logs`.

Overlay live shortcuts:

- `Ctrl+Shift+H`: hide/show overlay.
- `Ctrl+Shift+Q`: close overlay.
- `Ctrl+Shift+D`: toggle the compact debug/status line.

### Real-time advice mode

The GSI overlay uses an in-memory advice scheduler designed for about 40-50 short hints during a full match. It converts the latest GSI state into advice types such as `LOW_HP`, `LOW_HP_WARNING`, `RECENT_DAMAGE_WARNING`, `OVERSTAY_WARNING`, `DEATH_REVIEW`, `REPEATED_DEATH_PATTERN`, `LOW_MANA`, `DISABLED_STATUS`, `HERO_SURVIVABILITY_RISK`, `BUYBACK_AVAILABLE`, `SMOKED_STATUS`, `FARMING_PHASE_PRESSURE`, `OBJECTIVE_FIGHT_CHECK`, `BAD_FIGHT_RISK`, `ITEM_TIMING`, `SAFE_FARMING`, or `NO_ADVICE`.

Scheduling rules:

- Regular coaching advice is spaced by Dota game time, normally at least 45-60 seconds apart.
- Urgent `LOW_HP` advice uses a 15-second cooldown and can interrupt regular advice.
- Repeated identical state/category/action advice is suppressed with compact hashes and game-time windows.
- `NO_ADVICE` returns no recommendation and never calls an LLM.
- Recent lane damage can trigger `RECENT_DAMAGE_WARNING`, and low-HP overstay can trigger `OVERSTAY_WARNING`.
- Death review advice is event-driven, bypasses normal cooldown, and stays pinned while dead or respawning.
- `BUYBACK_AVAILABLE` is conservative: it appears only when the hero is dead, buyback is available, and late-game/base/objective context is serious enough. It does not tell the player to buy back aggressively.
- The last useful card stays visible during cooldown as `active_advice` instead of being replaced by empty monitoring.
- During laning, soft status states return `monitoring` with `Monitoring lane — no urgent advice.` instead of a full card.
- During cooldown, the overlay response includes `message: "Monitoring..."` so the desktop overlay stays visibly alive without flashing advice.

The overlay is fallback-first: rule-based advice is returned immediately, then optional LLM refinement can update wording later if the state is still current. LLM calls are optional, never required for core advice, and must not block the overlay. Groq `openai/gpt-oss-120b` is the recommended runtime model from the offline benchmark flow; the rule-based fallback still remains the safety layer.

Telemetry:

```bash
curl http://127.0.0.1:8000/overlay/stats
curl http://127.0.0.1:8000/overlay/debug/state_machine
```

Scheduler accounting check:

```bash
cd backend
python scripts/check_overlay_scheduler_accounting.py
```

Manual curl verification from the repository root:

```bash
curl -X POST http://127.0.0.1:8000/session/reset
curl http://127.0.0.1:8000/overlay/stats

# SOFT_STATUS / monitoring should keep advice_count at 0.
curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/generic_carry_safe_laning.json
curl http://127.0.0.1:8000/overlay/recommendation

# Full advice should increment advice_count to 1.
curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/juggernaut_laning_low_hp_warning.json
curl http://127.0.0.1:8000/overlay/recommendation

# Repeating the same state should return cooldown/duplicate and keep advice_count at 1.
curl http://127.0.0.1:8000/overlay/recommendation

# Switching to a different match id should start fresh, so the next full advice is count 1, not 2.
curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/antimage_laning_low_hp_warning.json
curl http://127.0.0.1:8000/overlay/recommendation

curl -X POST http://127.0.0.1:8000/session/reset
curl http://127.0.0.1:8000/overlay/stats
```

### Hero profiles and laning advice

Hero lane and safety context is data-driven through `data/heroes/hero_profiles.json`. Profiles define carry archetype, lane profile, low/critical HP thresholds, rough laning last-hit bands, and key escape or defensive abilities.

The live detector uses those profiles for universal lane coaching:

- `LOW_HP_WARNING`: HP is low but not critical during lane/early game.
- `ABILITY_SAFETY_COOLDOWN`: a profile safety tool is unavailable while HP or lane pressure makes trading risky.
- `LANING_FARM_CHECK`: last hits are clearly below the profile's rough lane threshold.
- `SOFT_STATUS`: stable lane state; the overlay shows a small monitoring line instead of a full card.

This avoids one-off hero logic in the detector. Unknown profile data falls back to generic carry rules, and no build or patch-meta advice is generated.

### Match advice simulation

You can simulate a 40-minute carry match without Dota:

```bash
cd backend
python scripts/simulate_match_advice.py
```

The simulation reads `data/match_simulations/carry_match_40min.jsonl`, feeds the states through the current decision point, advice policy, scheduler, and UX guard, then saves a JSON report under `backend/simulation_results/`.

By default it does not call external APIs. Set `SIMULATION_USE_LLM=true` only when you explicitly want to test optional LLM refinement.

For fair offline fallback-vs-LLM comparison on fast replay timelines, use blocking LLM mode:

```bash
SIMULATION_USE_LLM=true \
SIMULATION_LLM_BLOCKING=true \
USE_LLM=true \
LLM_PROVIDER=llamacpp \
LLAMACPP_BASE_URL=http://127.0.0.1:8080 \
LLAMACPP_MODEL=local-gpt-oss-20b \
python scripts/simulate_match_advice.py \
  --simulation-file ../data/match_simulations/replay_gsi_like_juggernaut_0_10.jsonl
```

You can also pass `--llm-blocking` instead of `SIMULATION_LLM_BLOCKING=true`. Blocking mode is only for offline simulation. It calls the LLM synchronously for eligible full advice events, keeps local priority/time-window policy overrides, and avoids live overlay stale-response behavior caused by processing hundreds of states instantly. Urgent low-HP and death review advice intentionally skip LLM and are counted as `llm_skipped_by_policy_count`; status/monitoring responses are not full advice events and never call LLM.

The terminal summary includes total advice shown, advice per 10 minutes, urgent/coaching/no-advice counts, rate-limit and duplicate suppression counts, fallback count, optional LLM count/applied rate, blocking-mode timeout/invalid/rejected/skip counts, stale response count, tactical hash changes, and whether the run fits the 40-50 hints-per-match target.

By default the simulation also exports manual review files:

- `backend/simulation_results/advice_review_<timestamp>.csv`
- `backend/simulation_results/advice_review_<timestamp>.md`

Use these files to rate every shown advice from a carry player's perspective. Set `SIMULATION_EXPORT_REVIEW=false` to skip review export. Set `SIMULATION_REVIEW_ONLY_SHOWN=false` to include `NO_ADVICE` and suppressed states too.

Suggested rating scale:

- `5` = useful and timely
- `4` = useful but generic
- `3` = harmless but weak
- `2` = poorly timed or too abstract
- `1` = harmful or misleading

### Comparing fallback and local LLM simulations

Run the same replay simulation once with fallback only and once with local llama.cpp blocking mode, then compare the generated JSON reports.

Fallback:

```bash
cd backend
SIMULATION_EXPORT_REVIEW=true \
SIMULATION_REVIEW_ONLY_SHOWN=true \
SIMULATION_USE_LLM=false \
python scripts/simulate_match_advice.py \
  --simulation-file ../data/match_simulations/replay_gsi_like_juggernaut_0_10.jsonl
```

Local LLM blocking:

```bash
SIMULATION_EXPORT_REVIEW=true \
SIMULATION_REVIEW_ONLY_SHOWN=true \
SIMULATION_USE_LLM=true \
SIMULATION_LLM_BLOCKING=true \
USE_LLM=true \
LLM_PROVIDER=llamacpp \
LLAMACPP_BASE_URL=http://127.0.0.1:8080 \
LLAMACPP_MODEL=local-gpt-oss-20b \
LLM_TIMEOUT=6 \
LLM_MAX_TOKENS=700 \
python scripts/simulate_match_advice.py \
  --simulation-file ../data/match_simulations/replay_gsi_like_juggernaut_0_10.jsonl
```

Comparison:

```bash
python scripts/compare_simulation_reports.py --latest-two
```

If the latest two reports are ambiguous, pass paths explicitly:

```bash
python scripts/compare_simulation_reports.py \
  --fallback-report simulation_results/match_advice_simulation_FALLBACK.json \
  --llm-report simulation_results/match_advice_simulation_LLM.json \
  --output-md simulation_results/comparison_fallback_vs_llm.md \
  --output-csv simulation_results/comparison_fallback_vs_llm.csv
```

The comparison report includes a Markdown summary table, optional CSV, decision-point distributions, and deterministic coursework-style interpretation. It explains whether the LLM changed advice wording without changing advice frequency, whether blocking mode avoided stale responses, and whether local policy still controlled priority and time window.

### Offline real match advice review

You can import a public OpenDota match for offline simulation testing. This is a manual review tool only; the live overlay does not call OpenDota during a real match.

```bash
cd backend
python scripts/import_opendota_match.py --match-id 1234567890 --interval-seconds 60
```

The importer saves the raw OpenDota response under `backend/imported_matches/` and writes a generated simulation file like:

```text
data/match_simulations/opendota_match_1234567890.jsonl
```

Then run the normal simulation against the imported match:

```bash
python scripts/simulate_match_advice.py --simulation-file ../data/match_simulations/opendota_match_1234567890.jsonl
```

Optional player selection:

```bash
python scripts/import_opendota_match.py --match-id 1234567890 --player-slot 0
python scripts/import_opendota_match.py --match-id 1234567890 --account-id 123456
```

Dense first-N-minutes replay:

```bash
python scripts/import_opendota_match.py \
  --match-id 8824199563 \
  --player-slot 131 \
  --interval-seconds 1 \
  --start-minute 0 \
  --end-minute 10 \
  --output ../data/match_simulations/opendota_match_8824199563_first10sec.jsonl

SIMULATION_EXPORT_REVIEW=true \
SIMULATION_REVIEW_ONLY_SHOWN=true \
python scripts/simulate_match_advice.py \
  --simulation-file ../data/match_simulations/opendota_match_8824199563_first10sec.jsonl
```

For 1-second timelines, OpenDota still provides some fields only per minute. The importer interpolates gold, carries forward XP/last-hit timelines, keeps HP conservative around death windows, and writes the inference note into `event_context`. The simulator reports dense-run metrics such as `states_per_minute`, `advice_per_minute`, `active_advice_count`, `monitoring_count`, `pinned_advice_count`, and repeated advice suppression so you can check that high-frequency replay does not create advice spam.

### Offline replay event adapter

For offline `.dem` evaluation, the MVP uses a replay-event adapter instead of parsing live game memory. The converter accepts combat-log-style JSONL events and writes **GSI-like replay states** for the existing simulator. This output is not identical to live GSI.

```bash
cd backend

python scripts/generate_replay_event_sample.py \
  --output ../data/replay_events/synthetic_juggernaut_lane_events.jsonl

python scripts/convert_replay_events_to_gsi_like.py \
  --events-jsonl ../data/replay_events/synthetic_juggernaut_lane_events.jsonl \
  --hero "Juggernaut" \
  --player-slot 1 \
  --start-minute 0 \
  --end-minute 10 \
  --interval-seconds 1 \
  --output ../data/match_simulations/replay_gsi_like_synthetic_juggernaut_0_10.jsonl

python scripts/simulate_match_advice.py \
  --simulation-file ../data/match_simulations/replay_gsi_like_synthetic_juggernaut_0_10.jsonl
```

Expected replay event format:

```json
{"timestamp_seconds":125,"type":"damage","player_slot":131,"hero":"Kez","data":{"damage_percent":25,"hp_after_percent":55}}
```

Simulation reports include `source_type` and `context_confidence_distribution`, so replay-derived states can be reviewed separately from OpenDota or synthetic simulations. See `backend/replay_tools/README.md` for the combat log export path and the future Clarity/Manta parser path.

Use the generated `advice_review_<timestamp>.csv` or `.md` file to manually rate whether the advice was useful for the selected carry player. Review exports include team context columns such as selected team, nearby teamfight result, recent allied/enemy deaths, objective type/team, whether the objective helped the selected team, and objective context.

Limitations: OpenDota replay data does not provide full live map context, vision, player intent, or exact HP at every moment. Imported advice is therefore conservative macro/carry advice based on timeline heuristics, not a reconstruction of complete live decision-making. When teamfight/objective data is missing, the importer marks context as `team_status_unknown` and keeps advice cautious.

Item timing detection for imported matches is configured in `data/meta/item_timing_rules.json`. The importer ignores starting items, consumables, minor components, recipes, neutral items, and small stat pieces, then marks only meaningful completed or semi-core carry timings such as Battle Fury, Mage Slayer, Desolator, Black King Bar, Manta Style, Disperser, Butterfly, or similar high-value items. Timing advice stays generic: it helps the player reassess farm, pressure, or objective value without recommending a build or saying to buy an item.

### Offline Dota replay parsing

The project includes an offline parser adapter:

```text
backend/scripts/parse_dota_demo_to_replay_events.py
```

It wraps an offline parser command, normalizes that output to
`replay_events.jsonl`, and then reuses the existing converter and simulator. A
minimal Clarity-based helper is available in `backend/replay_tools/clarity/`.
If no parser command is configured, the adapter exits with a clear error and
does not generate fake events.

Find local replays:

```bash
find ~/.steam ~/.local/share/Steam ~/Steam ~/Games \
  -type f \( -iname "*.dem" -o -iname "*.dem.bz2" \) \
  -printf '%TY-%Tm-%Td %TH:%TM %s %p\n' 2>/dev/null \
  | sort -r \
  | head -20
```

Download the known test replay if needed:

```bash
mkdir -p data/replays
curl -L \
  "http://replay251.valve.net/570/8824199563_895334157.dem.bz2" \
  -o data/replays/8824199563_895334157.dem.bz2
```

Build the Clarity helper:

```bash
cd backend/replay_tools/clarity
./build.sh
cd ../../..
```

The generated `dota-replay-events.jar` and Gradle build outputs are ignored by
git. The helper extracts conservative combat-log events and selected-hero
entity snapshots when Clarity exposes them exactly.

### Replay parser entity snapshot upgrade

The Clarity helper can emit one selected-hero `snapshot` event per second with
exact entity fields such as HP, mana, level, position, and alive/dead state. It
uses `--player-slot` through `CDOTA_PlayerResource` first and falls back to hero
class matching. Use `--debug-entities` to print whether the hero entity was
found, which fields exist, and how many snapshots were emitted.

```bash
java -jar backend/replay_tools/clarity/dota-replay-events.jar \
  --demo data/replays/8824199563_895334157.dem \
  --hero "Kez" \
  --player-slot 131 \
  --start 0 \
  --end 600 \
  --snapshot-interval 1 \
  --debug-entities \
  --output /tmp/replay_events_debug.jsonl
```

The converter marks exact snapshot fields as available in
`extra_context.available_signals` and removes them from `missing_signals`.
Combat-log damage pressure remains secondary context. The helper still does not
invent current spendable gold or ability cooldowns if those fields are not
available from the replay entity path. Last hits and denies are read from replay
team-data entities when those exact fields are present.

Offline replay-derived advice remains conservative. Isolated utility events
such as Tango, Branches, Quelling Blade, courier transfers, or small components
should not become full advice by themselves.

Laning Coach v1 combines farm pace, HP pressure, and position risk instead of
emitting generic farm reminders. It also suppresses repeated laning categories
for a short window unless HP becomes critical, lane pressure changes, or the
last-hit deficit gets meaningfully worse.

### Signal availability and limits

The backend records a capability matrix in each normalized state under
`extra_context`:

- `capability_source`
- `available_signals`
- `partial_signals`
- `missing_signals`
- `context_confidence`

Live Dota GSI can provide local-player signals such as HP, mana, gold, level,
last hits, items, ability cooldowns when the `abilities` block is present,
position, alive/respawn state, score changes, and buildings when the `buildings`
block is present. It does not provide reliable nearby ally/enemy positions,
enemy positions, or exact teamfight intent. Objective context is therefore only
partial and advice remains conservative.

Minimal Clarity replay parsing is weaker than live GSI. It can now provide
selected-hero HP, mana, level, position, alive/dead snapshots, and last-hit
counts when Clarity exposes the relevant entities, plus event timing, purchases,
ability/item use, and damage/heal windows. It still does not currently
reconstruct exact current spendable gold, ability cooldowns, nearby units, or
exact teamfight context. Replay advice should not use cooldown-specific survival
logic unless those exact signals are present.

OpenDota imports provide useful offline timelines for farm, items, kills,
deaths, objectives, and teamfights, but they still cannot reconstruct live
vision, nearby units, exact HP/mana, or player intent. Synthetic samples may
include exact test values, but they are evaluation fixtures rather than live
signals.

Configure the helper command:

```bash
export DOTA_DEMO_PARSER_COMMAND='java -jar backend/replay_tools/clarity/dota-replay-events.jar --demo {demo} --hero {hero} --player-slot {player_slot} --start {start_seconds} --end {end_seconds} --snapshot-interval 1 --output {output}'
```

Parse local replay:

```bash
cd backend
source .venv/bin/activate

python scripts/parse_dota_demo_to_replay_events.py \
  --demo "<DEMO_PATH>" \
  --hero "Juggernaut" \
  --player-slot 1 \
  --start-minute 0 \
  --end-minute 10 \
  --output ../data/match_simulations/replay_events_real_demo_0_10.jsonl
```

Or try match id. The script first checks local/OpenDota JSON files such as `../match_<id>.json`, `../data/opendota/match_<id>.json`, and `backend/imported_matches/opendota_match_<id>_raw.json`. If a `replay_url` is available, it downloads the replay to `../data/replays/`.

```bash
python scripts/parse_dota_demo_to_replay_events.py \
  --match-id 8824199563 \
  --hero "Kez" \
  --player-slot 131 \
  --start-minute 0 \
  --end-minute 10 \
  --output ../data/match_simulations/replay_events_match_8824199563_0_10.jsonl
```

The parser command must write JSONL or JSON events to `{output}` or stdout. Missing fields should be omitted. Approximate fields must include `event_context` and `context_confidence`.

Known match 8824199563 command:

```bash
python scripts/parse_dota_demo_to_replay_events.py \
  --demo ../data/replays/8824199563_895334157.dem.bz2 \
  --hero "Kez" \
  --player-slot 131 \
  --start-minute 0 \
  --end-minute 10 \
  --output ../data/match_simulations/replay_events_match_8824199563_0_10.jsonl
```

Convert to GSI-like 1-second states:

```bash
python scripts/convert_replay_events_to_gsi_like.py \
  --events-jsonl ../data/match_simulations/replay_events_real_demo_0_10.jsonl \
  --hero "Juggernaut" \
  --player-slot 1 \
  --start-minute 0 \
  --end-minute 10 \
  --interval-seconds 1 \
  --output ../data/match_simulations/replay_gsi_like_real_demo_0_10.jsonl
```

Known match 8824199563 conversion:

```bash
python scripts/convert_replay_events_to_gsi_like.py \
  --events-jsonl ../data/match_simulations/replay_events_match_8824199563_0_10.jsonl \
  --hero "Kez" \
  --player-slot 131 \
  --start-minute 0 \
  --end-minute 10 \
  --interval-seconds 1 \
  --output ../data/match_simulations/replay_gsi_like_match_8824199563_0_10.jsonl
```

Run fallback simulation:

```bash
SIMULATION_EXPORT_REVIEW=true \
SIMULATION_REVIEW_ONLY_SHOWN=true \
SIMULATION_USE_LLM=false \
python scripts/simulate_match_advice.py \
  --simulation-file ../data/match_simulations/replay_gsi_like_real_demo_0_10.jsonl
```

Known match 8824199563 fallback simulation:

```bash
SIMULATION_EXPORT_REVIEW=true \
SIMULATION_REVIEW_ONLY_SHOWN=true \
SIMULATION_USE_LLM=false \
python scripts/simulate_match_advice.py \
  --simulation-file ../data/match_simulations/replay_gsi_like_match_8824199563_0_10.jsonl
```

Run local LLM blocking simulation:

```bash
SIMULATION_EXPORT_REVIEW=true \
SIMULATION_REVIEW_ONLY_SHOWN=true \
SIMULATION_USE_LLM=true \
SIMULATION_LLM_BLOCKING=true \
USE_LLM=true \
LLM_PROVIDER=llamacpp \
LLAMACPP_BASE_URL=http://127.0.0.1:8080 \
LLAMACPP_MODEL=local-gpt-oss-20b \
LLM_TIMEOUT=6 \
LLM_MAX_TOKENS=700 \
python scripts/simulate_match_advice.py \
  --simulation-file ../data/match_simulations/replay_gsi_like_real_demo_0_10.jsonl
```

Known match 8824199563 local LLM blocking simulation:

```bash
SIMULATION_EXPORT_REVIEW=true \
SIMULATION_REVIEW_ONLY_SHOWN=true \
SIMULATION_USE_LLM=true \
SIMULATION_LLM_BLOCKING=true \
USE_LLM=true \
LLM_PROVIDER=llamacpp \
LLAMACPP_BASE_URL=http://127.0.0.1:8080 \
LLAMACPP_MODEL=local-gpt-oss-20b \
LLM_TIMEOUT=6 \
LLM_MAX_TOKENS=700 \
python scripts/simulate_match_advice.py \
  --simulation-file ../data/match_simulations/replay_gsi_like_match_8824199563_0_10.jsonl
```

Show latest report and review:

```bash
REPORT=$(ls -t simulation_results/match_advice_simulation_*.json | head -1)
REVIEW=$(ls -t simulation_results/advice_review_*.md | head -1)

cat "$REPORT"
sed -n '1,220p' "$REVIEW"
```

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
  "action": "Avoid contesting pressure and move to safer farm.",
  "reason": "Enemy pressure is active. A low-value fight or death delays your next timing.",
  "risk": "High risk if you farm visible areas or force a fight.",
  "priority": "high",
  "time_window": "next 60-90 seconds",
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

### Universal carry policy sample scenarios

```bash
curl -X POST http://127.0.0.1:8000/recommend \
  -H "Content-Type: application/json" \
  -d @../data/scenarios/phantom_assassin_low_hp.json

curl -X POST http://127.0.0.1:8000/recommend \
  -H "Content-Type: application/json" \
  -d @../data/scenarios/drow_ranger_pressure.json

curl -X POST http://127.0.0.1:8000/recommend \
  -H "Content-Type: application/json" \
  -d @../data/scenarios/sven_objective_fight.json

curl -X POST http://127.0.0.1:8000/recommend \
  -H "Content-Type: application/json" \
  -d @../data/scenarios/antimage_calm_farming.json
```

### POST /gsi — Minimal simulated GSI update

```bash
curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d '{
    "map": {"clock_time": 840, "game_state": "DOTA_GAMERULES_STATE_GAME_IN_PROGRESS"},
    "player": {"gold": 1800},
    "hero": {
      "name": "npc_dota_hero_antimage",
      "level": 10,
      "health_percent": 30,
      "alive": true
    },
    "items": {
      "slot0": {"name": "item_power_treads"},
      "slot1": {"name": "item_ring_of_health"}
    }
  }'
```

### Simulate GSI with sample payloads

Start the backend, then post a sample from the repository root:

```bash
curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/low_hp_juggernaut.json

curl http://127.0.0.1:8000/overlay/recommendation
```

Available samples:

- `data/gsi_samples/low_hp_juggernaut.json` — triggers `LOW_HP`.
- `data/gsi_samples/antimage_pressure_14min.json` — triggers `FARMING_PHASE_PRESSURE`.
- `data/gsi_samples/luna_objective_fight.json` — triggers `OBJECTIVE_FIGHT_CHECK`.
- `data/gsi_samples/calm_farming_antimage.json` — triggers `SAFE_FARMING`.
- `data/gsi_samples/unsupported_hero.json` — returns `unsupported_hero` status in the overlay.
- `data/gsi_samples/low_mana.json` — triggers `LOW_MANA`.
- `data/gsi_samples/disabled_status.json` — triggers `DISABLED_STATUS`.
- `data/gsi_samples/dead_buyback_available.json` — triggers `BUYBACK_AVAILABLE`.
- `data/gsi_samples/smoked_status.json` — triggers `SMOKED_STATUS`.
- `data/gsi_samples/low_farm_rate.json` — triggers `FARMING_PHASE_PRESSURE`.
- `data/gsi_samples/medusa_low_mana.json` — triggers `HERO_SURVIVABILITY_RISK`.
- `data/gsi_samples/antimage_blink_cooldown.json` — triggers `HERO_SURVIVABILITY_RISK`.
- `data/gsi_samples/juggernaut_blade_fury_cooldown.json` — triggers `ABILITY_SAFETY_COOLDOWN`.
- `data/gsi_samples/lifestealer_rage_cooldown.json` — triggers `ABILITY_SAFETY_COOLDOWN`.
- `data/gsi_samples/death_antimage_before.json` + `death_antimage_after.json` — triggers death review for Blink cooldown death.
- `data/gsi_samples/repeated_death_*.json` — triggers repeated death pattern after the second death.
- `data/gsi_samples/medusa_low_mana_death_before.json` + `medusa_low_mana_death_after.json` — triggers low-resource death review.
- `data/gsi_samples/juggernaut_laning_low_hp_warning.json` — triggers `LOW_HP_WARNING`.
- `data/gsi_samples/juggernaut_blade_fury_cooldown_lane.json` — triggers `ABILITY_SAFETY_COOLDOWN`.
- `data/gsi_samples/juggernaut_low_lh_min5.json` — triggers `LANING_FARM_CHECK`.
- `data/gsi_samples/juggernaut_safe_lane_status.json` — returns `monitoring` / `SOFT_STATUS`.
- `data/gsi_samples/antimage_laning_low_hp_warning.json` — triggers `LOW_HP_WARNING`.
- `data/gsi_samples/medusa_low_mana_laning.json` — triggers `HERO_SURVIVABILITY_RISK`.
- `data/gsi_samples/lifestealer_rage_cooldown_lane.json` — triggers `ABILITY_SAFETY_COOLDOWN`.
- `data/gsi_samples/slark_pounce_cooldown_lane.json` — triggers `HERO_SURVIVABILITY_RISK`.
- `data/gsi_samples/generic_carry_safe_laning.json` — returns `monitoring` / `SOFT_STATUS`.
- `data/gsi_samples/juggernaut_trade_damage_1.json` + `juggernaut_trade_damage_2.json` — triggers `RECENT_DAMAGE_WARNING`.
- `data/gsi_samples/juggernaut_trade_damage_3.json` — triggers urgent `LOW_HP`.
- `data/gsi_samples/juggernaut_death_after_overstay.json` — triggers death review after deaths increase.
- `data/gsi_samples/juggernaut_second_death_after_overstay.json` — triggers `REPEATED_DEATH_PATTERN`.

Safety-window wording checks:

```bash
# Expected action: "Reset mana before taking an extended fight."
curl -X POST http://127.0.0.1:8000/session/reset
curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/medusa_low_mana_laning.json
curl http://127.0.0.1:8000/overlay/recommendation

# Expected action: "Avoid committing forward until Pounce is ready."
curl -X POST http://127.0.0.1:8000/session/reset
curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/slark_pounce_cooldown_lane.json
curl http://127.0.0.1:8000/overlay/recommendation

# Expected action: "Avoid risky trades until Rage is ready."
curl -X POST http://127.0.0.1:8000/session/reset
curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/lifestealer_rage_cooldown_lane.json
curl http://127.0.0.1:8000/overlay/recommendation

# Expected action: "Avoid risky trades until Blade Fury is ready."
curl -X POST http://127.0.0.1:8000/session/reset
curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/juggernaut_blade_fury_cooldown_lane.json
curl http://127.0.0.1:8000/overlay/recommendation
```

Live GSI sample curls:

```bash
curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/low_mana.json

curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/disabled_status.json

curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/dead_buyback_available.json

curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/smoked_status.json

curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/low_farm_rate.json

curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/medusa_low_mana.json

curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/antimage_blink_cooldown.json

curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/juggernaut_blade_fury_cooldown.json

curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/lifestealer_rage_cooldown.json

curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/juggernaut_laning_low_hp_warning.json

curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/juggernaut_blade_fury_cooldown_lane.json

curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/juggernaut_low_lh_min5.json

curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/juggernaut_safe_lane_status.json

for sample in \
  antimage_laning_low_hp_warning.json \
  medusa_low_mana_laning.json \
  lifestealer_rage_cooldown_lane.json \
  slark_pounce_cooldown_lane.json \
  generic_carry_safe_laning.json; do
  curl -X POST http://127.0.0.1:8000/gsi \
    -H "Content-Type: application/json" \
    -d @data/gsi_samples/$sample
  curl http://127.0.0.1:8000/overlay/recommendation
done
```

Death review sequence:

```bash
curl -X POST http://127.0.0.1:8000/session/reset

curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/death_antimage_before.json

curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/death_antimage_after.json

curl http://127.0.0.1:8000/overlay/recommendation
curl http://127.0.0.1:8000/session/memory
```

Expected: `DEATH_WITH_ESCAPE_ON_COOLDOWN` or a generic `DEATH_REVIEW` if context is incomplete.

Repeated death sequence:

```bash
curl -X POST http://127.0.0.1:8000/session/reset

curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/repeated_death_1_before.json
curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/repeated_death_1_after.json
curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/repeated_death_2_before.json
curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/repeated_death_2_after.json

curl http://127.0.0.1:8000/overlay/recommendation
curl http://127.0.0.1:8000/session/memory
```

Expected: `REPEATED_DEATH_PATTERN`.

Live lane state-machine sequence:

```bash
curl -X POST http://127.0.0.1:8000/session/reset

# Baseline lane state: monitoring, advice_count stays 0.
curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/juggernaut_trade_damage_1.json
curl http://127.0.0.1:8000/overlay/recommendation

# Heavy HP drop: expected RECENT_DAMAGE_WARNING.
curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/juggernaut_trade_damage_2.json
curl http://127.0.0.1:8000/overlay/recommendation

# Polling again during cooldown should keep the useful card visible as active_advice.
curl http://127.0.0.1:8000/overlay/recommendation

# Critical HP: expected LOW_HP, bypassing normal cooldown.
curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/juggernaut_trade_damage_3.json
curl http://127.0.0.1:8000/overlay/recommendation

# Death with deaths counter increase: expected DEATH_LOW_RESOURCE or DEATH_REVIEW, pinned while dead.
curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/juggernaut_death_after_overstay.json
curl http://127.0.0.1:8000/overlay/recommendation

# Second death in the same session: expected REPEATED_DEATH_PATTERN.
curl -X POST http://127.0.0.1:8000/gsi \
  -H "Content-Type: application/json" \
  -d @data/gsi_samples/juggernaut_second_death_after_overstay.json
curl http://127.0.0.1:8000/overlay/recommendation

# Inspect why the state machine chose the current card.
curl http://127.0.0.1:8000/overlay/debug/state_machine
```

### Inspecting live GSI data

Use the debug endpoints to see what Dota 2 is actually sending during a live player match:

```bash
curl http://127.0.0.1:8000/gsi/debug/latest
curl http://127.0.0.1:8000/gsi/debug/fields
```

`/gsi/debug/latest` returns the latest raw GSI payload, latest normalized state, top-level keys, and detected sections such as `map`, `player`, `hero`, `items`, `abilities`, `buildings`, `draft`, and `provider`.

`/gsi/debug/fields` returns a compact field summary:

```json
{
  "has_map": true,
  "has_player": true,
  "has_hero": true,
  "has_items": true,
  "has_abilities": true,
  "has_buildings": false,
  "has_draft": false,
  "available_hero_fields": ["alive", "health_percent", "level", "name"],
  "available_player_fields": ["gold"],
  "available_map_fields": ["clock_time", "game_state"]
}
```

To save raw GSI payload samples locally, set this in `backend/.env` and restart the backend:

```text
GSI_DEBUG_LOG=true
```

Samples are written to `backend/gsi_debug_samples/`, which is ignored by git.

### Live GSI available fields

Live Dota 2 GSI can provide rich local player and hero state, including:

- map fields such as `clock_time`, `game_time`, `radiant_score`, `dire_score`, `game_state`, `daytime`, and `paused`;
- player fields such as gold, kills/deaths/assists, last hits, denies, GPM, XPM, player slot, and team name;
- hero fields such as health, mana, alive/respawn state, position, status effects, smoke state, buyback cost/cooldown, and Aghanim flags;
- items, abilities, and sometimes buildings.

The live overlay uses these fields for player-focused advice such as low HP, low mana, disabled status, buyback checks, smoke discipline, hero-specific safety windows, and simple farm-rate checks. GSI still does not provide reliable full enemy intent, full team readiness, or strategic map plans, so live advice remains conservative.

In lobby or demo mode, Dota may send `matchid=0` and unrealistic values such as very high gold or GPM. The backend treats this as local demo mode, sets the normalized match id to `local_demo`, ignores unrealistic farm values for farm-rate advice, and avoids carrying match-memory death conclusions from previous tests.

Hero profiles live in `data/heroes/hero_profiles.json`. They currently cover broad carry archetypes and simple safety mechanics such as Medusa mana, Anti-Mage Blink, Juggernaut Blade Fury, Lifestealer Rage, Slark Dark Pact/Pounce, Morphling mobility/Attribute Shift, Phantom Assassin Blur, Drow Gust, Sven Warcry, Kez mobility/defensive windows, and generic ranged carry safety. These profiles only constrain advice; they do not create aggressive hero-specific calls or item/build recommendations.

The live session also keeps short in-memory match history. It detects alive-to-dead transitions and records compact death context such as pre-death HP/mana, safety flags, status effects, items, GPM, last hits, and rough event context. Death review advice is shown at most once per death event and remains conservative:

- repeated deaths: reset the next route and avoid repeating the same risky path;
- escape/defensive cooldown deaths: wait for the key escape or defensive tool before committing;
- low-resource deaths: reset earlier when HP, mana, or hero survivability resources get low;
- unknown deaths: use respawn time to plan a safer route.

Session debug:

```bash
curl http://127.0.0.1:8000/session/memory
curl http://127.0.0.1:8000/overlay/debug/state_machine
curl -X POST http://127.0.0.1:8000/session/reset
```

### GET /state/current

```bash
curl http://127.0.0.1:8000/state/current
```

Before any GSI data arrives, this returns:

```json
{
  "status": "waiting_for_gsi",
  "timestamp": null,
  "state": null
}
```

### GET /overlay/recommendation

```bash
curl http://127.0.0.1:8000/overlay/recommendation
```

The endpoint returns a compact wrapper with `status`, `event`, `timestamp`, and `recommendation`. If no decision point is detected, `recommendation` is `null`. Non-urgent overlay advice is rate-limited, but active advice may be returned as `active_advice` so useful cards do not disappear into empty monitoring.

---

## Dota 2 GSI Setup

Create this file:

```text
gamestate_integration_dota_ai_coach.cfg
```

Place it in Dota 2's GSI config directory:

```text
game/dota/cfg/gamestate_integration/
```

Example config:

```text
"Dota 2 Integration Configuration"
{
  "uri" "http://127.0.0.1:8000/gsi"
  "timeout" "5.0"
  "buffer" "0.1"
  "throttle" "0.5"
  "heartbeat" "30.0"
  "data"
  {
    "provider" "1"
    "map" "1"
    "player" "1"
    "hero" "1"
    "items" "1"
    "abilities" "0"
    "buildings" "0"
    "draft" "0"
    "wearables" "0"
  }
}
```

Start the FastAPI server before launching Dota 2:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

Then open the overlay page at `http://127.0.0.1:8000/frontend/overlay.html`.

---

## How it Works

1. **Input validation** — Pydantic checks every field (type, range, allowed values).
2. **RAG retrieval** — All `.md` files in `data/knowledge_base/` are split into paragraphs and the top 3 most keyword-relevant paragraphs for the current situation are extracted.
3. **Fallback recommender** — Profile-aware fallback wording produces a structured recommendation from the local advice policy.
4. **GSI normalization** — `POST /gsi` stores the latest raw payload in memory and normalizes hero, minute, level, gold, items, HP, game state, and team status where possible.
5. **Decision points** — The overlay flow detects survival, death review, hero safety, laning, farm, objective, item timing, and status states such as `LOW_HP`, `LOW_HP_WARNING`, `ABILITY_SAFETY_COOLDOWN`, `LANING_FARM_CHECK`, `HERO_SURVIVABILITY_RISK`, `FARMING_PHASE_PRESSURE`, `SAFE_FARMING`, `SOFT_STATUS`, or `NO_ADVICE`.
6. **Advice policy** — Local universal carry policy controls priority, time window, and safety constraints.
7. **Optional LLM provider** — If Groq, OpenRouter, or llama.cpp is configured and the state has an actionable decision point, the backend tries an LLM recommendation. Invalid or unavailable LLM output falls back automatically.
8. **Logging** — Every generated recommendation is saved as a timestamped JSON file in `backend/logs/`, including the input, decision point, RAG context, provider, model, source, output, and any LLM fallback reason.

### Validation Notes

- MVP-1 supports a carry-focused hero list driven by `data/heroes/hero_profiles.json`, including Anti-Mage, Juggernaut, Lifestealer, Medusa, Slark, Morphling, Phantom Assassin, Drow Ranger, Luna, Sven, Kez, Ursa, Monkey King, Spectre, Terrorblade, Phantom Lancer, Naga Siren, Sniper, Muerta, Gyrocopter, and Ember Spirit.
- Item names are trimmed before processing.
- Empty item names, such as `""` or `"   "`, are rejected.
- Retrieved knowledge-base context is filtered so it does not add timing hints that contradict already-owned items.

---

## Roadmap

| Version | Feature |
|---------|---------|
| MVP-1 *(current)* | Rule-based fallback, local keyword RAG, JSON logging, GSI overlay, Electron desktop overlay, LLM provider (Groq/OpenRouter/llama.cpp), replay parser, launcher |
| MVP-2 | Embedding-based semantic RAG (sentence-transformers or similar) |
| MVP-3 | OpenDota/STRATZ API integration for real match data |
| MVP-4 | Full Windows packaging and installer |

---

## Requirements

- Python 3.11+
- FastAPI 0.111
- Uvicorn 0.30
- Pydantic 2.7
