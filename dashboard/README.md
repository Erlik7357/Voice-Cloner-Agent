# Dashboard Quick Start

1. Start backend API:
```bash
set VOICE_CLONER_GPU=0
.venv311/Scripts/python backend/tts_server.py
```

2. Start dashboard:
```bash
cd dashboard
npm install
npm run dev
```

Open http://localhost:5173

Backend API expected at http://localhost:5000.

Optional:
- Set custom API URL with `VITE_API_BASE_URL` (defaults to `http://localhost:5000`).
- Use root shortcut script: `start_dashboard_local.bat`
