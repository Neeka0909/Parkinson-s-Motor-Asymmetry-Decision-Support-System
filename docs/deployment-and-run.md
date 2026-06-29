# Deployment & Run Guide

This guide covers how to run the Nipun stack locally, via Docker, and how to prepare for production deployment.

> **Disclaimer:** Nipun is a decision-support research tool. It does not diagnose Parkinson's Disease. All outputs must be reviewed by a qualified neurologist.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Environment Variables](#environment-variables)
4. [Option A — Local Development (Recommended for First Run)](#option-a--local-development-recommended-for-first-run)
5. [Option B — Docker (Full Stack)](#option-b--docker-full-stack)
6. [Mobile App (Expo)](#mobile-app-expo)
7. [ML Model Training](#ml-model-training)
8. [Verify the Stack](#verify-the-stack)
9. [Production Deployment Notes](#production-deployment-notes)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| **Python** | 3.11+ (3.13 supported) | Backend API & ML training |
| **Node.js** | 18+ | React Native / Expo mobile app |
| **npm** | 9+ | Mobile package manager |
| **Docker Desktop** | Latest | PostgreSQL & optional full-stack container run |
| **Git** | Any recent version | Clone / version control |

**Optional (mobile testing):**

- [Expo Go](https://expo.dev/go) app on a physical phone
- Android Studio emulator or Xcode simulator

**Windows note:** Use PowerShell. Replace `cp` with `copy` if needed:

```powershell
copy .env.example .env
```

---

## Project Structure

```
Nipun/
├── backend/          Flask REST API
├── mobile/           React Native (Expo) app
├── ml/               Scikit-learn training & model files
├── docs/             Architecture & API documentation
├── docker-compose.yml
└── .env.example
```

**Default ports:**

| Service | Port |
|---------|------|
| Flask API | `5000` |
| PostgreSQL | `5432` |
| Expo dev server | `8081` (Metro) |

---

## Environment Variables

### Root `.env` (backend)

Copy from the project root:

```powershell
copy .env.example .env
```

| Variable | Example | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://nipun:nipun_secret@localhost:5432/nipun_db` | PostgreSQL connection string |
| `FLASK_APP` | `app` | Flask application entry |
| `FLASK_ENV` | `development` | Set to `production` in prod |
| `SECRET_KEY` | Random string | Flask session secret |
| `JWT_SECRET_KEY` | Random string | JWT signing key |
| `ML_MODEL_PATH` | `../ml/models/risk_classifier.joblib` | Path to trained classifier |

### Mobile `.env`

Copy inside the `mobile/` folder:

```powershell
cd mobile
copy .env.example .env
```

| Variable | Example | Description |
|----------|---------|-------------|
| `EXPO_PUBLIC_API_URL` | `http://192.168.1.10:5000/api/v1` | Backend API base URL |

**Important:** When testing on a **physical phone**, use your PC's LAN IP — not `localhost`. Example:

```
EXPO_PUBLIC_API_URL=http://192.168.1.10:5000/api/v1
```

Find your IP on Windows:

```powershell
ipconfig
```

Look for `IPv4 Address` under your active network adapter.

---

## Option A — Local Development (Recommended for First Run)

Run each service separately. Best for debugging backend and mobile together.

### Step 1 — Start PostgreSQL

```powershell
cd d:\Project\Nipun
docker compose up -d db
```

Wait until the database is healthy:

```powershell
docker compose ps
```

You should see the `db` service as `healthy`.

### Step 2 — Install & Run Backend

```powershell
cd d:\Project\Nipun\backend
pip install -r requirements.txt
python init_db.py
python run.py
```

The API starts at **http://localhost:5000**.

Health check:

```powershell
curl http://localhost:5000/api/v1/health
```

Expected response:

```json
{"status": "ok", "service": "nipun-backend"}
```

### Step 3 — Train ML Model (First Time Only)

Open a **new terminal**:

```powershell
cd d:\Project\Nipun\ml
pip install -r requirements.txt
python train.py
```

Model is saved to `ml/models/risk_classifier.joblib`. Restart the backend if it was already running so it picks up the model file.

### Step 4 — Run Mobile App

Open a **new terminal**:

```powershell
cd d:\Project\Nipun\mobile
npm install
npx expo start
```

Then:

- Press **`a`** for Android emulator
- Press **`i`** for iOS simulator (macOS only)
- Scan the QR code with **Expo Go** on your phone

---

## Option B — Docker (Full Stack)

Runs PostgreSQL and the Flask backend in containers.

### Step 1 — Train the ML Model First

The backend container mounts `ml/models/`. Train locally before starting Docker:

```powershell
cd d:\Project\Nipun\ml
pip install -r requirements.txt
python train.py
```

### Step 2 — Start All Services

```powershell
cd d:\Project\Nipun
docker compose up -d --build
```

This starts:

- **db** — PostgreSQL 16 on port `5432`
- **backend** — Flask/Gunicorn on port `5000`

### Step 3 — Initialize Database Tables

```powershell
docker compose exec backend python init_db.py
```

### Step 4 — Check Logs

```powershell
docker compose logs -f backend
```

### Stop Services

```powershell
docker compose down
```

To remove database data as well:

```powershell
docker compose down -v
```

---

## Mobile App (Expo)

### First Launch Flow

1. Open the app → **Register** a new account (age 50+).
2. Read and acknowledge the **clinical disclaimer**.
3. Play any of the three games:
   - **Bubble Pop** — reaction time
   - **Piano Tiles** — flight time
   - **Typing Race** — hold time & hand dynamics
4. View **Progress** → **Run Analysis** for risk profile.
5. Generate a **PDF Report** for neurologist review.

### API URL by Environment

| Where the app runs | `EXPO_PUBLIC_API_URL` |
|--------------------|------------------------|
| Same machine (web/emulator on PC) | `http://localhost:5000/api/v1` |
| Physical phone on same Wi‑Fi | `http://<YOUR_PC_IP>:5000/api/v1` |
| Production server | `https://your-domain.com/api/v1` |

After changing `.env`, restart Expo:

```powershell
npx expo start -c
```

The `-c` flag clears the Metro cache.

---

## ML Model Training

Training uses a **synthetic proxy dataset** for academic validation (not real patient data).

```powershell
cd d:\Project\Nipun\ml
pip install -r requirements.txt
python train.py
```

Output:

- Model file: `ml/models/risk_classifier.joblib`
- Console: classification report (precision/recall per risk tier)

Test inference standalone:

```powershell
python inference.py
```

Risk tiers: `baseline` → `monitor` → `elevated` → `referral`

If the model file is missing, the backend falls back to **rule-based scoring** automatically.

---

## Verify the Stack

### 1. Health Check

```powershell
curl http://localhost:5000/api/v1/health
```

### 2. Register a Test User

```powershell
curl -X POST http://localhost:5000/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"test@nipun.lk\",\"password\":\"test12345\",\"full_name\":\"Test User\",\"age\":68,\"handedness\":\"right\",\"language_pref\":\"mixed\"}'
```

Save the `access_token` from the response.

### 3. Submit a Game Session

```powershell
curl -X POST http://localhost:5000/api/v1/games/sessions `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer <YOUR_TOKEN>" `
  -d '{\"game_type\":\"bubble_pop\",\"device_orientation\":\"portrait\",\"time_of_day\":\"morning\",\"score\":450,\"duration_ms\":30000,\"raw_events\":[{\"type\":\"tap\",\"x\":100,\"y\":400,\"hand_side\":\"left\",\"timestamp_ms\":1000,\"reaction_time_ms\":380,\"hit\":true}],\"started_at\":\"2026-06-27T08:00:00Z\",\"completed_at\":\"2026-06-27T08:00:30Z\"}'
```

### 4. Run Analysis

```powershell
curl -X POST http://localhost:5000/api/v1/predictions/analyze `
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

### 5. Generate PDF Report

```powershell
curl -X POST http://localhost:5000/api/v1/reports/generate `
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

PDFs are written to `backend/app/reports/`.

---

## Production Deployment Notes

This project is configured for **research/demo** use. Before any real clinical deployment:

### Security Checklist

- [ ] Change `SECRET_KEY` and `JWT_SECRET_KEY` to strong random values
- [ ] Use HTTPS (TLS) via a reverse proxy (Nginx, Caddy, or cloud load balancer)
- [ ] Never expose PostgreSQL port `5432` publicly
- [ ] Use managed PostgreSQL (AWS RDS, Azure Database, Supabase, etc.)
- [ ] Set `FLASK_ENV=production` and disable Flask debug mode
- [ ] Add rate limiting and request validation at the proxy layer

### Suggested Production Architecture

```
Mobile App (Expo EAS build)
        │
        ▼ HTTPS
  Reverse Proxy (Nginx / Caddy)
        │
        ▼
  Gunicorn (backend container)
        │
        ├── PostgreSQL (managed)
        └── ML model volume (risk_classifier.joblib)
```

### Backend (Gunicorn)

The Docker image already uses Gunicorn:

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--reload", "run:app"]
```

For production, remove `--reload` and add workers:

```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 run:app
```

### Mobile (Expo EAS)

Build standalone apps for distribution:

```powershell
cd mobile
npm install -g eas-cli
eas build --platform android
eas build --platform ios
```

Set `EXPO_PUBLIC_API_URL` in EAS environment secrets to your production API URL.

### Cloud Options

| Component | Options |
|-----------|---------|
| Backend | Railway, Render, AWS ECS, Azure App Service, DigitalOcean App Platform |
| Database | AWS RDS, Supabase, Neon, Azure PostgreSQL |
| Mobile builds | Expo EAS |
| File storage (PDFs) | S3, Azure Blob (replace local `backend/app/reports/`) |

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'flask'`

Install backend dependencies:

```powershell
cd backend
pip install -r requirements.txt
```

### `scikit-learn` or `numpy` fails to install (Python 3.13)

Use the versions in the current `requirements.txt` (flexible `>=` pins with prebuilt wheels). Do not downgrade to pinned `1.5.0` / `1.26.4` on Python 3.13.

### `psycopg2-binary` build error on Python 3.13

Ensure `psycopg2-binary>=2.9.10` is in `backend/requirements.txt`.

### Mobile app cannot reach API

1. Confirm backend is running: `curl http://localhost:5000/api/v1/health`
2. Use your PC's LAN IP in `mobile/.env`, not `localhost`
3. Allow port `5000` through Windows Firewall
4. Phone and PC must be on the **same Wi‑Fi network**
5. Restart Expo with cache clear: `npx expo start -c`

### Database connection refused

1. Check Docker is running: `docker compose ps`
2. Start DB: `docker compose up -d db`
3. Verify `DATABASE_URL` in `.env` matches Docker credentials

### ML predictions always use rule-based fallback

1. Train the model: `python ml/train.py`
2. Confirm file exists: `ml/models/risk_classifier.joblib`
3. Check `ML_MODEL_PATH` in `.env` points to that file
4. Restart the backend

### `flask db upgrade` not found

This project uses `init_db.py` instead of Alembic migrations for initial setup:

```powershell
cd backend
python init_db.py
```

---

## Quick Reference — Start Everything

**Terminal 1 — Database & Backend:**

```powershell
cd d:\Project\Nipun
docker compose up -d db
cd backend
python init_db.py
python run.py
```

**Terminal 2 — Mobile:**

```powershell
cd d:\Project\Nipun\mobile
npx expo start
```

**One-time — ML model:**

```powershell
cd d:\Project\Nipun\ml
python train.py
```

---

## Related Documentation

- [API Contract](./api-contract.md)
- [Database Schema](./database-schema.md)
- [Feature Matrix](./feature-matrix.md)
- [Phase 5 Testing Guide](./phase5-testing.md)
