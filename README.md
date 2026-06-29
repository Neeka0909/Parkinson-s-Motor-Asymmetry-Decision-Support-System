# Parkinson's Motor Asymmetry Decision-Support System

A mobile-based longitudinal decision-support system for early Parkinson's Disease asymmetry detection using gamified motor-keystroke dynamics.

> **Disclaimer:** This application provides exploratory digital biomarker data only. It does not diagnose, treat, or replace clinical evaluation by a qualified neurologist.

## Architecture

```
mobile/          React Native (Expo) — gamified assessments, tap/keystroke logging
backend/         Python Flask — REST API, auth, scoring, PDF reports
ml/              Scikit-learn — feature engineering, risk classification
docs/            Feature matrix, schema, API contract, literature review
```

## Quick Start

See **[Deployment & Run Guide](docs/deployment-and-run.md)** for full setup instructions (local, Docker, mobile, ML, and production notes).

### Prerequisites

- Docker & Docker Compose
- Node.js 18+
- Python 3.11+ (3.13 supported)

### 1. Start database & backend

```powershell
copy .env.example .env
docker compose up -d db
cd backend
pip install -r requirements.txt
python init_db.py
python run.py
```

### 2. Train ML model (synthetic validation data)

```powershell
cd ml
pip install -r requirements.txt
python train.py
```

### 3. Start mobile app

```powershell
cd mobile
npm install
npx expo start
```

## Assessment Games

| Game | Biomarkers |
|------|------------|
| Bubble Pop | Reaction Time, spatial coordination |
| Piano Tiles | Flight Time, lateral processing speed |
| Typing Race | Hold Time, inter-key flight time, hand asymmetry |

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
