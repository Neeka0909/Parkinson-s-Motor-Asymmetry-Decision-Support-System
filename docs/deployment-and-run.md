# Deployment & Run Guide

Complete setup guide for **Motor DSS** — local development, Docker, mobile (Expo Go), ML training, and production notes.

> **Disclaimer:** This system is a decision-support research tool. It does not diagnose Parkinson's Disease. All outputs must be reviewed by a qualified neurologist.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Environment Variables](#environment-variables)
4. [Option A — Local Development (Recommended)](#option-a--local-development-recommended)
5. [Option B — Docker Full Stack](#option-b--docker-full-stack)
6. [Mobile App (Expo)](#mobile-app-expo)
7. [ML Model Training](#ml-model-training)
8. [Verify the Stack](#verify-the-stack)
9. [Production Deployment Notes](#production-deployment-notes)
10. [Troubleshooting](#troubleshooting)
11. [Quick Reference](#quick-reference)

---

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| **Docker Desktop** | Latest | Must be **running** before any `docker compose` command |
| **Python** | 3.11+ (3.13 tested) | Backend API & ML training |
| **Node.js** | 18+ | Expo / React Native mobile app |
| **npm** | 9+ | Mobile dependencies |

**For mobile testing (pick one):**

| Method | Requirements |
|--------|--------------|
| **Physical phone (recommended)** | [Expo Go](https://expo.dev/go) app, phone + PC on same Wi‑Fi |
| **Android emulator** | Android Studio, SDK, `ANDROID_HOME` env var |
| **iOS simulator** | macOS + Xcode only |

**Windows:** Use PowerShell. Use `copy` instead of `cp` for file copies.

---

## Project Structure

```
<project-root>/
├── .env                 Backend environment (copy from .env.example)
├── docker-compose.yml   PostgreSQL + optional backend container
├── backend/             Flask REST API
│   ├── init_db.py       Create database tables
│   └── run.py           Start dev server (0.0.0.0:5000)
├── mobile/              Expo SDK 56 app ("Motor DSS")
│   └── .env             Mobile API URL (copy from .env.example)
├── ml/                  Scikit-learn training & model
│   └── models/          risk_classifier.joblib (after train.py)
└── docs/                Architecture & API documentation
```

### Ports

| Service | Host port | Notes |
|---------|-----------|-------|
| Flask API | `5000` | Binds to `0.0.0.0` — reachable from phone via LAN IP |
| PostgreSQL (Docker) | **`15432`** | Maps to container port `5432` |
| Expo Metro | `8081` | Dev bundler |

> **Why port 15432?** Many Windows machines already run local PostgreSQL on ports **5432** and **5433**. Using `15432` ensures Docker Postgres is reachable without conflict. Always use **`127.0.0.1:15432`** in `DATABASE_URL`, not `localhost`.

---

## Environment Variables

### Root `.env` (backend)

```powershell
copy .env.example .env
```

| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | `postgresql://pdapp:pdapp_secret@127.0.0.1:15432/pdapp_db` | Docker Postgres connection |
| `FLASK_APP` | `app` | Flask entry point |
| `FLASK_ENV` | `development` | Set `production` in prod |
| `SECRET_KEY` | Random string | Flask secret |
| `JWT_SECRET_KEY` | Random string | JWT signing key |
| `ML_MODEL_PATH` | `../ml/models/risk_classifier.joblib` | Trained classifier path |

The backend loads `.env` from the project root automatically (see `backend/app/config.py`).

### Mobile `.env`

```powershell
cd mobile
copy .env.example .env
```

| Variable | Example | Description |
|----------|---------|-------------|
| `EXPO_PUBLIC_API_URL` | `http://192.168.100.243:5000/api/v1` | Flask API base URL |

**Critical for physical phones:**

| Target | `EXPO_PUBLIC_API_URL` |
|--------|------------------------|
| Phone on same Wi‑Fi | `http://<YOUR_PC_IP>:5000/api/v1` |
| Emulator on same PC | `http://localhost:5000/api/v1` or `http://10.0.2.2:5000/api/v1` (Android) |
| Production | `https://your-domain.com/api/v1` |

Find your PC IP:

```powershell
ipconfig
```

Use the **IPv4 Address** of your Wi‑Fi adapter (e.g. `192.168.100.243`).

After editing `mobile/.env`, restart Expo with cache clear:

```powershell
npx expo start --lan -c
```

---

## Option A — Local Development (Recommended)

### Step 1 — Start Docker Desktop

Ensure Docker Desktop is running. Verify:

```powershell
docker info
```

If you see `Cannot connect to the Docker daemon` or `dockerDesktopLinuxEngine` pipe error, start Docker Desktop and wait until it shows **Running**.

### Step 2 — Start PostgreSQL

```powershell
cd <project-root>
copy .env.example .env
docker compose up -d db
docker compose ps
```

Wait until the `db` service shows **healthy**.

### Step 3 — Install & initialize backend

```powershell
cd <project-root>\backend
pip install -r requirements.txt
python init_db.py
python run.py
```

Expected output includes `Running on http://0.0.0.0:5000`.

Health check (PowerShell):

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/v1/health
```

Expected:

```json
{"status": "ok", "service": "motor-dss-backend"}
```

### Step 4 — Train ML model (first time)

New terminal:

```powershell
cd <project-root>\ml
pip install -r requirements.txt
python train.py
```

Output: `Model saved to ...\ml\models\risk_classifier.joblib` (~89% accuracy on synthetic data).

Restart the backend if it was already running.

### Step 5 — Run mobile app

New terminal:

```powershell
cd <project-root>\mobile
copy .env.example .env
# Edit .env — set EXPO_PUBLIC_API_URL to your PC LAN IP
npm install
npx expo start --lan -c
```

- **Physical phone:** Scan QR code with Expo Go
- **Android emulator:** Press `a` (requires Android Studio + SDK — see [Troubleshooting](#android-sdk--emulator-errors))
- **Do not** open `http://127.0.0.1:8081` in a browser expecting the app UI — that URL serves the Expo manifest JSON

---

## Option B — Docker Full Stack

Runs PostgreSQL and Flask backend in containers.

### Step 1 — Train ML model locally first

```powershell
cd <project-root>\ml
pip install -r requirements.txt
python train.py
```

The backend container mounts `./ml/models/` as read-only.

### Step 2 — Start services

```powershell
cd <project-root>
docker compose up -d --build
```

| Container | Host access | Internal |
|-----------|-------------|----------|
| `db` | `127.0.0.1:15432` | `5432` |
| `backend` | `http://localhost:5000` | — |

### Step 3 — Initialize tables

```powershell
docker compose exec backend python init_db.py
```

### Step 4 — Logs & stop

```powershell
docker compose logs -f backend
docker compose down          # stop containers
docker compose down -v       # stop + delete database volume
```

---

## Mobile App (Expo)

**App name:** Motor DSS  
**Bundle ID:** `com.pdmotor.dss`  
**Expo SDK:** 56

### First-time user flow

1. **Register** — name, email, password, age (50+)
2. Read the **clinical disclaimer**
3. Play games: **Bubble Pop**, **Piano Tiles**, **Typing Race**
4. **Progress** → **Run Analysis** → risk profile
5. **Report** → generate PDF for neurologist

### Physical phone checklist

- [ ] Backend running: `python run.py` in `backend/`
- [ ] `mobile/.env` uses PC LAN IP, not `localhost`
- [ ] Phone and PC on **same Wi‑Fi** (not mobile data)
- [ ] Expo started with `npx expo start --lan -c`
- [ ] Windows Firewall allows inbound TCP on port **5000** (see Troubleshooting)

### Allow Flask through Windows Firewall (one-time, Admin PowerShell)

```powershell
New-NetFirewallRule -DisplayName "Motor DSS Flask" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

---

## ML Model Training

Uses a **synthetic proxy dataset** for academic validation (not real patient data).

```powershell
cd <project-root>\ml
pip install -r requirements.txt
python train.py
python inference.py
```

| Output | Location |
|--------|----------|
| Trained model | `ml/models/risk_classifier.joblib` |
| Risk tiers | `baseline` → `monitor` → `elevated` → `referral` |

If the model file is missing, the backend uses **rule-based scoring** automatically.

---

## Verify the Stack

### 1. Health check

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/v1/health
```

### 2. Register test user

```powershell
$body = @{
  email = "test@example.com"
  password = "test12345"
  full_name = "Test User"
  age = 68
  handedness = "right"
  language_pref = "mixed"
} | ConvertTo-Json

Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:5000/api/v1/auth/register" `
  -ContentType "application/json" -Body $body
```

Save the `access_token` from the response.

### 3. Submit a game session

Replace `<TOKEN>` with your access token:

```powershell
$session = @{
  game_type = "bubble_pop"
  device_orientation = "portrait"
  time_of_day = "morning"
  score = 450
  duration_ms = 30000
  raw_events = @(@{
    type = "tap"; x = 100; y = 400; hand_side = "left"
    timestamp_ms = 1000; reaction_time_ms = 380; hit = $true
  })
  started_at = "2026-06-27T08:00:00Z"
  completed_at = "2026-06-27T08:00:30Z"
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:5000/api/v1/games/sessions" `
  -ContentType "application/json" `
  -Headers @{ Authorization = "Bearer <TOKEN>" } `
  -Body $session
```

### 4. Run analysis & generate PDF

```powershell
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:5000/api/v1/predictions/analyze" `
  -Headers @{ Authorization = "Bearer <TOKEN>" }

Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:5000/api/v1/reports/generate" `
  -Headers @{ Authorization = "Bearer <TOKEN>" }
```

PDFs are saved to `backend/app/reports/`.

---

## Production Deployment Notes

Research/demo configuration only. Before clinical use:

### Security checklist

- [ ] Change `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] HTTPS via reverse proxy (Nginx, Caddy, cloud LB)
- [ ] Never expose PostgreSQL publicly
- [ ] Use managed PostgreSQL (RDS, Supabase, Neon, Azure)
- [ ] Set `FLASK_ENV=production`, disable Flask debug
- [ ] Rate limiting at proxy layer

### Architecture

```
Mobile (Expo EAS build)
        │ HTTPS
        ▼
  Reverse Proxy
        ▼
  Gunicorn (Flask)  :5000
        │
        ├── Managed PostgreSQL
        └── ML model (risk_classifier.joblib)
```

Production Gunicorn (no `--reload`):

```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 run:app
```

Mobile builds:

```powershell
npm install -g eas-cli
cd mobile
eas build --platform android
```

Set `EXPO_PUBLIC_API_URL` in EAS secrets to your production API URL.

---

## Troubleshooting

### Docker: `dockerDesktopLinuxEngine` pipe not found

**Cause:** Docker Desktop is not running.

**Fix:** Start Docker Desktop, wait until status is **Running**, then retry `docker compose up -d db`.

---

### Database: `password authentication failed for user "pdapp"`

**Cause:** Docker volume was initialized with old credentials, or connection hits local PostgreSQL instead of Docker.

**Fix A — Reset volume (deletes local DB data):**

```powershell
cd <project-root>
docker compose down -v
docker compose up -d db
cd backend
python init_db.py
```

**Fix B — Verify connection targets Docker:**

Ensure `.env` contains:

```
DATABASE_URL=postgresql://pdapp:pdapp_secret@127.0.0.1:15432/pdapp_db
```

Test:

```powershell
docker exec -it $(docker compose ps -q db) psql -U pdapp -d pdapp_db -c "SELECT 1"
```

---

### Mobile: `Network request failed` on register/login

**Cause:** `mobile/.env` uses `localhost`, which on a phone refers to the phone itself.

**Fix:**

1. Run `ipconfig` → get Wi‑Fi IPv4 (e.g. `192.168.100.243`)
2. Set `mobile/.env`:
   ```
   EXPO_PUBLIC_API_URL=http://192.168.100.243:5000/api/v1
   ```
3. Ensure backend is running (`python run.py`)
4. Restart Expo: `npx expo start --lan -c`
5. Add Windows Firewall rule for port 5000 (see [Mobile App section](#mobile-app-expo))

---

### Android SDK / emulator errors

```
Failed to resolve the Android SDK path
'adb' is not recognized
```

**Cause:** Android Studio / SDK not installed.

**Fix:** Use **Expo Go on a physical phone** (no SDK needed), or install [Android Studio](https://developer.android.com/studio), then set:

```powershell
[System.Environment]::SetEnvironmentVariable("ANDROID_HOME", "$env:LOCALAPPDATA\Android\Sdk", "User")
```

Add `%LOCALAPPDATA%\Android\Sdk\platform-tools` to PATH. Restart terminal.

---

### npm: `ECONNRESET` during `npm install`

**Cause:** Unstable network during large package download.

**Fix:**

```powershell
cd mobile
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
npm cache clean --force
npm install --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000
```

Close other programs locking `node_modules` if you see `EPERM` errors.

---

### Python 3.13: package build failures

Use flexible dependency pins already in `requirements.txt`:

- `numpy>=2.1.0`, `pandas>=2.2.3`, `scikit-learn>=1.5.2`
- `psycopg2-binary>=2.9.10`

Do **not** pin older versions (`numpy==1.26.4`, `scikit-learn==1.5.0`) on Python 3.13.

---

### ML predictions use rule-based fallback only

1. Run `python ml/train.py`
2. Confirm `ml/models/risk_classifier.joblib` exists
3. Check `ML_MODEL_PATH` in root `.env`
4. Restart backend

---

### Metro: `Cannot read properties of undefined (reading 'transformFile')`

**Cause:** `babel-preset-expo` is missing as a direct dependency (required for Expo SDK 56).

**Fix:**

```powershell
cd mobile
npx expo install babel-preset-expo
npx expo start --lan -c
```

---

### Expo Go: SDK version mismatch

**Cause:** Expo Go app version does not match project SDK.

**Fix:** This project uses **Expo SDK 56**. Ensure `mobile/package.json` has `"expo": "^56.0.0"` and run `npm install`. Restart with `npx expo start --lan -c`.

---

### `flask db upgrade` not found

This project uses `init_db.py` for table creation:

```powershell
cd backend
python init_db.py
```

---

## Quick Reference

**Terminal 1 — Database & backend:**

```powershell
cd <project-root>
docker compose up -d db
cd backend
python init_db.py
python run.py
```

**Terminal 2 — Mobile:**

```powershell
cd <project-root>\mobile
# Ensure .env has your PC LAN IP
npx expo start --lan -c
```

**One-time — ML model:**

```powershell
cd <project-root>\ml
python train.py
```

---

## Related Documentation

- [API Contract](./api-contract.md)
- [Database Schema](./database-schema.md)
- [Feature Matrix](./feature-matrix.md)
- [Literature Review](./literature-review.md)
- [Phase 5 Testing Guide](./phase5-testing.md)
