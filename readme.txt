Event Search App (Django + React)

This document explains how to run and test the application using Docker (recommended) or running locally without Docker, plus example API commands and troubleshooting notes.

1) Prerequisites (choose ONE path)
- Docker Desktop: install and start it, wait until it says "Docker is running".
OR
- Local (no Docker):
  - Python 3.11+
  - Node.js LTS (for the React dev server)

2) Clone and open the project
- Commands:
  git clone <your-repo-url>
  cd ASSIGNMENT

3) Option A: Run with Docker (recommended)
- Start services:
  docker compose up -d --build
- Verify:
  - Backend health: http://localhost:8000/api/health/
  - Frontend UI: http://localhost:5173
- Upload a file (PowerShell example):
  $FILE="$env:USERPROFILE\Downloads\events_sample.log"
  curl.exe -X POST "http://localhost:8000/api/upload/" -F ("files=@{0}" -f $FILE)
- Search (example: action=REJECT):
  curl.exe -s -H "Content-Type: application/json" -d "{ \"criteria\": { \"action\": \"REJECT\" } }" http://localhost:8000/api/search/
- Use the UI:
  1) Open http://localhost:5173
  2) Upload event files
  3) Enter search field/value and optional starttime/endtime (epoch)
  4) View results, file name, and search time
- Stop:
  docker compose down

4) Option B: Run locally (no Docker)
- Backend:
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  pip install -r backend\requirements.txt
  python backend\manage.py migrate
  python backend\manage.py runserver 0.0.0.0:8001
  (Health: http://127.0.0.1:8001/api/health/)
- Frontend (new terminal):
  cd frontend
  $env:VITE_API_BASE = "http://127.0.0.1:8001/api"
  npm install
  npm run dev
  (UI: http://localhost:5173)
- Upload + search (local backend on 8001):
  $FILE="$env:USERPROFILE\Downloads\events_sample.log"
  curl.exe -X POST "http://127.0.0.1:8001/api/upload/" -F ("files=@{0}" -f $FILE)
  curl.exe -s -H "Content-Type: application/json" -d "{ \"criteria\": { \"action\": \"REJECT\" } }" http://127.0.0.1:8001/api/search/

5) Create a sample events file (if you do not have one yet)
- PowerShell commands:
  $FILE = "$env:USERPROFILE\Downloads\events_sample.log"
  "1|2|111111111111|eni-293216456|159.62.125.136|30.55.177.194|152|23475|8|1725850449|1725855086|REJECT|OK|80|443" | Set-Content -Encoding utf8 $FILE
  "2|2|111111111111|eni-XYZ|221.181.27.227|10.0.0.5|6|100|5000|1725851000|1725852000|ACCEPT|OK|12345|22" | Add-Content -Encoding utf8 $FILE

6) API quick commands
- Health (Docker):
  curl.exe http://localhost:8000/api/health/
- Health (Local no Docker):
  curl.exe http://127.0.0.1:8001/api/health/
- Upload (multipart):
  curl.exe -X POST "<BASE>/upload/" -F ("files=@{0}" -f "$env:USERPROFILE\Downloads\events_sample.log")
  (Replace <BASE> with http://localhost:8000/api or http://127.0.0.1:8001/api)
- Search by field:
  curl.exe -s -H "Content-Type: application/json" -d "{ \"criteria\": { \"action\": \"REJECT\" } }" <BASE>/search/
- Search with time window:
  curl.exe -s -H "Content-Type: application/json" -d "{ \"criteria\": { \"srcaddr\": \"159.62.125.136\" }, \"starttime\": 1725850449, \"endtime\": 1725855086 }" <BASE>/search/

7) Concurrency test (10 parallel searches)
- Docker backend on port 8000:
  $body = '{ "criteria": { "action": "REJECT" } }'
  $jobs = 1..10 | % { Start-Job { param($p) curl.exe -s -H "Content-Type: application/json" -d $p http://localhost:8000/api/search/ } -ArgumentList $body }
  Wait-Job $jobs | Out-Null; $jobs | Receive-Job; $jobs | Remove-Job
- Local backend on port 8001 (replace host/port accordingly).

8) Troubleshooting
- In PowerShell, use curl.exe (not curl) to avoid alias issues.
- Always include trailing slash on endpoints (e.g., /api/health/).
- If ports are busy, change backend port or free the conflicting process.
- For uploads, ensure the file path exists: Test-Path <path>.
- Docker engine issues: restart Docker Desktop, then run docker compose up -d --build again.

9) Git tips (.gitignore suggestions)
- Do not commit local runtime artifacts:
  venv/
  backend/data/
  backend/db.sqlite3
  frontend/node_modules/
  __pycache__/
  *.pyc

10) Notes
- The backend scans uploaded files concurrently for low-latency searches.
- Supported formats include JSONL and pipe-delimited rows similar to the sample above.

