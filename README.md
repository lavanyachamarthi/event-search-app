## Event Search App (Django + React)

This repository contains a simple, fast event search application with:
- Django REST backend (file upload, concurrent search)
- React.js frontend (upload/search UI)
- Optional Docker set up for one-command spin-up

### Features
- Upload one or more event log files to the backend storage.
- Search by multiple fields (e.g., `srcaddr`, `dstaddr`, `action`, `account-id`, etc.).
- Filter by time window using epoch `starttime` and `endtime`.
- Concurrent file scanning for low latency under concurrent load.
- UI displays matching events, source file name, and the total search time.

## Project Structure
```
ASSIGNMENT/
  backend/
    project/               # Django project (settings/urls)
    projectapi/            # Upload + Search API
    data/                  # Uploaded files (bind-mounted in Docker)
    requirements.txt       # Backend Python deps
    Dockerfile             # Backend image
    manage.py
  frontend/
    src/                   # React components
    package.json           # Frontend deps
    vite.config.js         # Vite config
    Dockerfile             # Frontend image
  docker-compose.yml       # Orchestrates backend + frontend
  requirements.txt         # Root-level Python deps (optional mirror)
  README.md
```

## Option A — Run with Docker (recommended)
### Prerequisites
- Install Docker Desktop and start it (ensure it says “Docker is running”).

### Start services
```powershell
cd <project-folder>   # e.g., C:\Users\<you>\Downloads\ASSIGNMENT
docker compose up -d --build
```

### Verify
- Backend health: `http://localhost:8000/api/health/`
- Frontend UI: `http://localhost:5173`

### Upload a file and search
```powershell
$FILE="$env:USERPROFILE\Downloads\events_sample.log"
curl.exe -X POST "http://localhost:8000/api/upload/" -F ("files=@{0}" -f $FILE)

curl.exe -s -H "Content-Type: application/json" \
  -d "{ \"criteria\": { \"action\": \"REJECT\" } }" \
  http://localhost:8000/api/search/
```

### Stop
```powershell
docker compose down
```

## Option B — Run Locally (no Docker)
### Prerequisites
- Python 3.11+
- Node.js LTS (for the React dev server)

### Backend
```powershell
cd <project-folder>
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
python backend/manage.py migrate
python backend/manage.py runserver 0.0.0.0:8001
```

Verify: `http://127.0.0.1:8001/api/health/`

### Frontend
```powershell
cd <project-folder>\frontend
$env:VITE_API_BASE = "http://127.0.0.1:8001/api"
npm install
npm run dev
```

Open: `http://localhost:5173`

## Event File Format
Supports JSONL or pipe-delimited lines. Example pipe-delimited line (fields auto-mapped):
```
1|2|111111111111|eni-293216456|159.62.125.136|30.55.177.194|152|23475|8|1725850449|1725855086|REJECT|OK|80|443
```
Key columns that can be searched include: `srcaddr`, `dstaddr`, `action`, `account-id`, `instance-id`, `starttime`, `endtime`, etc.

### Create a sample file (optional)
```powershell
$FILE = "$env:USERPROFILE\Downloads\events_sample.log"
"1|2|111111111111|eni-293216456|159.62.125.136|30.55.177.194|152|23475|8|1725850449|1725855086|REJECT|OK|80|443" | Set-Content -Encoding utf8 $FILE
"2|2|111111111111|eni-XYZ|221.181.27.227|10.0.0.5|6|100|5000|1725851000|1725852000|ACCEPT|OK|12345|22" | Add-Content -Encoding utf8 $FILE
```

## API Reference
Base URL (Docker): `http://localhost:8000/api/`  |  Base URL (Local): `http://127.0.0.1:8001/api/`

- Health: `GET /health/`
  - Response: `{ "status": "ok" }`

- Upload: `POST /upload/` (multipart/form-data)
  - Field: `files` (repeatable)
  - Example (PowerShell):
    ```powershell
    curl.exe -X POST "<BASE>/upload/" -F ("files=@{0}" -f "C:\\path\\to\\file.log")
    ```

- Search: `POST /search/` (application/json)
  - Request body:
    ```json
    {
      "criteria": { "srcaddr": "159.62.125.136" },
      "starttime": 1725850449,
      "endtime": 1725855086
    }
    ```
  - Response:
    ```json
    {
      "count": 3,
      "elapsed_seconds": 0.52,
      "results": [
        {
          "summary": "159.62.125.136 → 30.55.177.194 | Action: REJECT | Log Status: OK",
          "file": "events_2025.log",
          "event": { "...": "original parsed fields" }
        }
      ]
    }
    ```

## Concurrency & Performance Test
Sends 10 concurrent search requests to the backend (good for quick load checks):
```powershell
$body = '{ "criteria": { "action": "REJECT" } }'
$jobs = 1..10 | % { Start-Job { param($p) curl.exe -s -H "Content-Type: application/json" -d $p http://localhost:8000/api/search/ } -ArgumentList $body }
Wait-Job $jobs | Out-Null; $jobs | Receive-Job; $jobs | Remove-Job
```
For local (no Docker), replace `localhost:8000` with `127.0.0.1:8001`.

## Troubleshooting
- PowerShell aliasing: use `curl.exe` instead of `curl`.
- Always include trailing slash on Django endpoints: `/api/health/`.
- Port busy: change backend port or stop the conflicting process.
- Docker engine: if compose fails, restart Docker Desktop and try again.
- File upload errors: verify the local path with `Test-Path` and quote paths with spaces.

## Git Tips
Do not commit local runtime artifacts. Suggested `.gitignore` entries:
```
venv/
backend/data/
backend/db.sqlite3
frontend/node_modules/
__pycache__/
*.pyc
.DS_Store
```

## License
For educational/assessment use. Replace or add a license file if needed.


