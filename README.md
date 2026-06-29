# Parkinson's Motor Asymmetry Decision-Support System

**Motor DSS** — a mobile-based longitudinal decision-support system for early Parkinson's Disease asymmetry detection using gamified motor-keystroke dynamics.

> **Disclaimer:** This application provides exploratory digital biomarker data only. It does not diagnose, treat, or replace clinical evaluation by a qualified neurologist.

## Architecture

```
mobile/          React Native (Expo SDK 51) — gamified assessments, tap/keystroke logging
backend/         Python Flask — REST API, auth, scoring, PDF reports
ml/              Scikit-learn — feature engineering, risk classification
docs/            Feature matrix, schema, API contract, deployment guide
```

## Documentation

| Document | Description |
|----------|-------------|
| [Documentation Index](docs/README.md) | Full list of all docs |
| [Deployment & Run Guide](docs/deployment-and-run.md) | Full setup: Docker, backend, ML, mobile, troubleshooting |
| [API Contract](docs/api-contract.md) | REST endpoints |
| [Database Schema](docs/database-schema.md) | PostgreSQL tables |
| [Feature Matrix](docs/feature-matrix.md) | Digital biomarkers |
| [Literature Review](docs/literature-review.md) | Research background |
| [Phase 5 Testing](docs/phase5-testing.md) | Longitudinal simulation & acceptance criteria |

## Quick Start

See **[Deployment & Run Guide](docs/deployment-and-run.md)** for complete instructions.

### Prerequisites

- **Docker Desktop** (must be running before `docker compose` commands)
- **Python** 3.11+ (3.13 supported)
- **Node.js** 18+ and npm 9+
- **Expo Go** on your phone (recommended for mobile testing)

### 1. Environment files

```powershell
copy .env.example .env
cd mobile
copy .env.example .env
```

Edit `mobile/.env` — set `EXPO_PUBLIC_API_URL` to your PC's LAN IP when testing on a physical phone (see deployment guide).

### 2. Database & backend

```powershell
docker compose up -d db
cd backend
pip install -r requirements.txt
python init_db.py
python run.py
```

Backend runs at **http://0.0.0.0:5000** (health: `/api/v1/health`).

PostgreSQL (Docker) is exposed on host port **15432** (not 5432 — avoids conflict with local PostgreSQL installations).

### 3. ML model (first time)

```powershell
cd ml
pip install -r requirements.txt
python train.py
```

Model saved to `ml/models/risk_classifier.joblib`.

### 4. Mobile app

```powershell
cd mobile
npm install
npx expo start --lan -c
```

Scan the QR code with **Expo Go** on your phone (same Wi‑Fi as your PC).

## Assessment Games

| Game | Biomarkers |
|------|------------|
| Bubble Pop | Reaction Time, spatial coordination |
| Piano Tiles | Flight Time, lateral processing speed |
| Typing Race | Hold Time, inter-key flight time, hand asymmetry |

## Key Configuration

| Setting | Value |
|---------|-------|
| App name | Motor DSS |
| DB user / database | `pdapp` / `pdapp_db` |
| Docker Postgres port | `15432` → container `5432` |
| Flask API port | `5000` |
| Expo Metro port | `8081` |
| Backend service ID | `motor-dss-backend` |

## Project Phases

| Phase | Deliverable | Status |
|-------|-------------|--------|
| 1 | Literature review, feature matrix, UI/UX design | Complete |
| 2 | React Native games & keystroke logging | Complete |
| 3 | Flask API, PostgreSQL, Docker | Complete |
| 4 | Scikit-learn model training & inference | Complete |
| 5 | Longitudinal tracking, PDF reports, testing | Complete |

## License

Academic research project — not for clinical use without regulatory approval.
