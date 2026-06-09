# Windows Packaging Phase 1

This guide builds a portable Windows coursework-defense launcher for Dota AI Coach.

The packaged launcher does not read game memory, read the screen, automate input, use STRATZ, or inject into Dota 2. It starts local bundled tools only:

- `dota-ai-coach-backend.exe`
- `Dota AI Coach Overlay.exe`
- bundled replay demo JSONL files
- the existing GSI config helper

## Prerequisites

- Windows 11
- Python 3.11+
- Node.js LTS
- npm
- PowerShell

Build on Windows for Windows output. PyInstaller and Electron produce platform-specific binaries.

## 1. Build the backend executable

```powershell
cd C:\path\to\dota-ai-coach\backend
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
pip install pyinstaller
pyinstaller packaging\dota_ai_coach_backend.spec
```

Expected output:

```text
backend\dist\dota-ai-coach-backend\dota-ai-coach-backend.exe
backend\dist\dota-ai-coach-backend\dota-ai-coach-demo-playback.exe
```

The backend executable starts FastAPI on `127.0.0.1:8000` with access logs disabled. `USE_LLM=false` is the default unless the environment overrides it.

## 2. Build the desktop overlay

```powershell
cd C:\path\to\dota-ai-coach\frontend\desktop-overlay
npm install
npm run pack
```

Expected output:

```text
frontend\desktop-overlay\dist\win-unpacked\Dota AI Coach Overlay.exe
```

The launcher bundles this unpacked app as an extra resource.

## 3. Build the launcher

```powershell
cd C:\path\to\dota-ai-coach\frontend\launcher
npm install
npm run dist
```

Expected portable output:

```text
frontend\launcher\dist\Dota AI Coach Launcher-0.1.0-portable.exe
```

The launcher build includes:

- `backend\dist\dota-ai-coach-backend\`
- `frontend\desktop-overlay\dist\win-unpacked\`
- `data\match_simulations\replay_gsi_like_match_8843382732_pl_20_30.jsonl`
- `data\match_simulations\replay_gsi_like_match_8843471434_jugg_10_20.jsonl`
- `README.md`

## 4. Test packaged launcher

1. Run `Dota AI Coach Launcher-0.1.0-portable.exe`.
2. Click `Start Backend`.
3. Click `Start Overlay`.
4. Click `Demo: Phantom Lancer 20-30 macro`.
5. Confirm advice cards appear in the overlay.
6. Click `Stop Demo`.
7. Click `Stop Overlay`.
8. Click `Stop Backend`.

For live Dota GSI testing, use `Install / Check Dota GSI`. The generated config still points to:

```text
http://127.0.0.1:8000/gsi
```

## Packaged runtime paths

In development mode, the launcher keeps using:

- `backend\.venv` Python and `uvicorn`
- `frontend\desktop-overlay\npm run dev`
- repo-local `data\match_simulations`

In packaged mode, the launcher uses `process.resourcesPath`:

- `resources\backend\dota-ai-coach-backend.exe`
- `resources\backend\dota-ai-coach-demo-playback.exe`
- `resources\desktop-overlay\Dota AI Coach Overlay.exe`
- `resources\data\match_simulations\*.jsonl`

## Known limitations

- Phase 1 is portable packaging, not a signed installer.
- No code signing is configured.
- NSIS installer packaging is left for a later phase.
- Optional LLM runtime is not bundled; fallback-only demo mode is recommended for defense.
- The packaged demo uses bundled GSI-like replay states, not live Dota 2.
