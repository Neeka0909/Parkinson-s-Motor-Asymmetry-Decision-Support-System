# Motor DSS — Complete A–Z Technical Documentation

**Parkinson's Motor Asymmetry Decision-Support System**

| Field | Value |
|-------|-------|
| Document version | 2.0 |
| Application version | 1.0.0 |
| Application name | Motor DSS |
| Backend service ID | `motor-dss-backend` |
| API version | v1 (`/api/v1`) |
| Database | PostgreSQL 16 (Docker) |
| ML framework | scikit-learn Random Forest |
| Mobile stack | React Native 0.85.3 / Expo SDK 56 |
| Bundle ID | `com.pdmotor.dss` |
| Last updated | June 2026 |

> **Clinical disclaimer:** This system provides exploratory digital biomarker data for academic research and decision support only. It does **not** diagnose, treat, or replace clinical evaluation by a qualified neurologist. All outputs require professional medical review before any clinical action.

---

## Table of Contents

### Part I — Introduction & Context
1. [Executive Summary](#1-executive-summary)
2. [Research Background & Project Phases](#2-research-background--project-phases)
3. [System Goals & Non-Goals](#3-system-goals--non-goals)

### Part II — Architecture
4. [High-Level Architecture](#4-high-level-architecture)
5. [Component Interaction Diagrams](#5-component-interaction-diagrams)
6. [Complete Repository Structure](#6-complete-repository-structure)
7. [Technology Stack & Version Matrix](#7-technology-stack--version-matrix)

### Part III — Database System
8. [Database Overview & Docker Setup](#8-database-overview--docker-setup)
9. [Connection Strings & Configuration](#9-connection-strings--configuration)
10. [Schema Initialization](#10-schema-initialization)
11. [Entity-Relationship Model](#11-entity-relationship-model)
12. [Table Specifications](#12-table-specifications)
13. [How the Database Links to Each Component](#13-how-the-database-links-to-each-component)

### Part IV — Backend API
14. [Backend Application Structure](#14-backend-application-structure)
15. [Authentication & Security Model](#15-authentication--security-model)
16. [REST API Reference](#16-rest-api-reference)
17. [Biomarker Extraction Service](#17-biomarker-extraction-service)
18. [Feature Engineering Pipeline](#18-feature-engineering-pipeline)
19. [PDF Report Generation](#19-pdf-report-generation)
20. [Exercise Recommendation System](#20-exercise-recommendation-system)

### Part V — Mobile Application
21. [Mobile Stack & Configuration](#21-mobile-stack--configuration)
22. [Screen Map & User Flow](#22-screen-map--user-flow)
23. [Assessment Games](#23-assessment-games)
24. [Event Capture & Raw Event Schema](#24-event-capture--raw-event-schema)
25. [Mobile API Client](#25-mobile-api-client)
26. [Expo SDK 56 Upgrade Notes](#26-expo-sdk-56-upgrade-notes)

### Part VI — Machine Learning
27. [ML Pipeline Overview](#27-ml-pipeline-overview)
28. [Training Dataset (Synthetic)](#28-training-dataset-synthetic)
29. [Feature Vector Specification](#29-feature-vector-specification)
30. [Model Architecture & Hyperparameters](#30-model-architecture--hyperparameters)
31. [Training Procedure](#31-training-procedure)
32. [Model Artifact Format](#32-model-artifact-format)
33. [Inference Engine & Rule-Based Fallback](#33-inference-engine--rule-based-fallback)
34. [Risk Tiers & Clinical Recommendations](#34-risk-tiers--clinical-recommendations)
35. [Train vs Inference Data Gap](#35-train-vs-inference-data-gap)

### Part VII — Operations
36. [Complete Setup Guide (A–Z)](#36-complete-setup-guide-az)
37. [Environment Variables Reference](#37-environment-variables-reference)
38. [Deployment Modes](#38-deployment-modes)
39. [Verification & Testing](#39-verification--testing)
40. [Troubleshooting Encyclopedia](#40-troubleshooting-encyclopedia)
41. [Production Deployment Checklist](#41-production-deployment-checklist)

### Part VIII — Reference
42. [End-to-End Sequence Flows](#42-end-to-end-sequence-flows)
43. [Known Limitations & Future Work](#43-known-limitations--future-work)
44. [Glossary](#44-glossary)
45. [File Reference Index](#45-file-reference-index)
46. [Related Documentation](#46-related-documentation)

---

# Part I — Introduction & Context

## 1. Executive Summary

Motor DSS is a **longitudinal decision-support platform** for detecting early Parkinson's Disease (PD) motor asymmetry patterns using gamified digital biomarkers. The system captures sub-millisecond tap and keystroke dynamics from three mobile assessment games, stores them in PostgreSQL, aggregates longitudinal feature vectors, and classifies users into four risk tiers using a scikit-learn Random Forest classifier.

### What the system does

| Capability | Description |
|------------|-------------|
| Motor assessment | Three gamified tests: Bubble Pop, Piano Tiles, Typing Race |
| Biomarker extraction | Reaction Time, Flight Time, Hold Time, asymmetry ratios |
| Longitudinal tracking | 60-day rolling windows, trend detection, streak tracking |
| Risk classification | 4-tier output: baseline → monitor → elevated → referral |
| Clinician reports | PDF generation via ReportLab |
| Exercise guidance | Bilingual (English/Sinhala) recommendations by risk tier |

### Four main components

| Component | Directory | Runtime | Role |
|-----------|-----------|---------|------|
| Mobile app | `mobile/` | Expo Go / device | Games, event capture, REST client |
| Backend API | `backend/` | Flask (Python) | Auth, biomarkers, ML, PDF |
| Database | Docker | PostgreSQL 16 | Persistent storage |
| ML pipeline | `ml/` | Offline Python | Train classifier → `.joblib` artifact |

---

## 2. Research Background & Project Phases

Motor asymmetry — preferential slowing or reduced dexterity on one side of the body — is an early indicator of PD. This project implements a mobile-based longitudinal tracking system inspired by literature on keystroke dynamics, reaction time variability, and hand asymmetry in neurodegenerative conditions.

### Project phase deliverables

| Phase | Deliverable | Status |
|-------|-------------|--------|
| 1 | Literature review, feature matrix, UI/UX design | Complete |
| 2 | React Native games & keystroke logging | Complete |
| 3 | Flask API, PostgreSQL, Docker | Complete |
| 4 | Scikit-learn model training & inference | Complete |
| 5 | Longitudinal tracking, PDF reports, testing | Complete |

See [Literature Review](./literature-review.md) for research references and [Phase 5 Testing](./phase5-testing.md) for acceptance criteria.

---

## 3. System Goals & Non-Goals

### Goals

- Capture reproducible digital motor biomarkers from consumer mobile devices
- Store raw events for audit and reprocessing
- Aggregate longitudinal trends over weeks
- Provide exploratory risk stratification for neurologist review
- Generate downloadable PDF decision-support reports
- Support bilingual exercise recommendations (English + Sinhala)

### Non-goals

- Clinical diagnosis or FDA/regulatory approval
- Real-time continuous monitoring (sessions are discrete)
- Integration with hospital EHR systems
- Training on real patient clinical datasets (uses synthetic proxy data)
- Replacing in-person neurological examination

---

# Part II — Architecture

## 4. High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    MOBILE — Expo React Native (SDK 56)                       │
│                                                                              │
│   LoginScreen ── RegisterScreen ── HomeScreen ── GameScreen                 │
│        │                              │              │                       │
│        │                              ├── ProgressScreen                     │
│        │                              ├── ReportScreen                       │
│        │                              └── ExercisesScreen                    │
│        │                                                                     │
│   SecureStore (JWT)  ←──  api.ts (fetch)  ←──  EventLogger (raw events)     │
└────────────────────────────────────┬─────────────────────────────────────────┘
                                     │ HTTP REST  /api/v1  (Bearer JWT)
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         BACKEND — Flask (Python 3.11+)                       │
│                                                                              │
│   routes.py ──┬── biomarker_service.py    (raw_events → biomarkers)         │
│               ├── feature_engineering.py   (DB → 13-feature vector)          │
│               ├── ml_service.py            (vector → risk profile)           │
│               ├── report_service.py        (ReportLab PDF)                   │
│               └── exercise_service.py      (risk → exercise catalog)         │
│                                                                              │
│   models.py (SQLAlchemy ORM) ── psycopg2 ── PostgreSQL                      │
└────────────────────────────────────┬─────────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    DATABASE — PostgreSQL 16 (Docker)                         │
│                                                                              │
│   users │ game_logs │ biomarkers │ ai_predictions │ reports │ exercise_plans│
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                    ML TRAINING (offline, not runtime)                        │
│                                                                              │
│   train.py → generate_synthetic_data(2000) → RandomForest → .joblib         │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Component Interaction Diagrams

### Game session ingest

```
Mobile GameScreen
    │ EventLogger.events[]
    ▼
POST /api/v1/games/sessions  { game_type, raw_events, score, ... }
    ▼
routes.create_session()
    ├── INSERT game_logs (raw_events as JSON — audit trail preserved)
    ├── extract_biomarkers(game_type, raw_events)
    └── INSERT biomarkers[] (one row per extracted metric)
    ▼
Response 201: { session_id, biomarkers[] }
```

### ML analysis pipeline

```
POST /api/v1/predictions/analyze
    ▼
MLInferenceEngine.predict(user_id)
    ├── build_feature_vector(user_id)
    │     └── SELECT game_logs + biomarkers (last 60 days)
    │           └── Compute 13 longitudinal features
    ├── model.predict_proba(vector)  OR  rule_based_fallback()
    └── Return { risk_profile, confidence, feature_summary, recommendation }
    ▼
INSERT ai_predictions
    ▼
Response 200
```

### Report generation

```
POST /api/v1/reports/generate
    ▼
MLInferenceEngine.predict()  (re-runs analysis)
    ▼
generate_pdf_report(user, features, prediction, sessions_summary)
    └── Saves to backend/app/reports/report_{user_id}_{timestamp}.pdf
    ▼
INSERT reports { pdf_path, summary }
    ▼
Response 201: { report_id, download_url }
```

---

## 6. Complete Repository Structure

```
Nipun/  (project root)
│
├── .env.example                 Backend environment template
├── .env                         Backend secrets (not in git)
├── .gitignore                   Ignores node_modules, .joblib, .env
├── docker-compose.yml           PostgreSQL + optional backend container
├── README.md                    Quick start & doc links
│
├── backend/                     Flask REST API
│   ├── Dockerfile               Python 3.11-slim + gunicorn
│   ├── init_db.py               db.create_all() schema bootstrap
│   ├── run.py                   Dev server entry (0.0.0.0:5000)
│   ├── requirements.txt         Python dependencies
│   └── app/
│       ├── __init__.py          App factory, blueprints, CORS, JWT
│       ├── config.py            DATABASE_URL, JWT, ML_MODEL_PATH
│       ├── models.py            SQLAlchemy ORM (6 tables)
│       ├── routes.py            All REST endpoints
│       ├── reports/             Generated PDF output (.gitkeep)
│       └── services/
│           ├── biomarker_service.py
│           ├── feature_engineering.py
│           ├── ml_service.py
│           ├── exercise_service.py
│           └── report_service.py
│
├── mobile/                      Expo React Native app
│   ├── App.tsx                  Root component, screen routing
│   ├── app.json                 Expo config (SDK 56, splash plugin)
│   ├── babel.config.js          babel-preset-expo
│   ├── expo-env.d.ts            Expo TypeScript types reference
│   ├── package.json             Dependencies (Expo SDK 56)
│   ├── tsconfig.json            Extends expo/tsconfig.base
│   ├── .env.example             EXPO_PUBLIC_API_URL template
│   ├── assets/
│   │   └── icon.png             App icon
│   └── src/
│       ├── components/
│       │   ├── BigButton.tsx
│       │   ├── DisclaimerBanner.tsx
│       │   └── ScreenContainer.tsx
│       ├── games/
│       │   ├── BubblePopGame.tsx
│       │   ├── PianoTilesGame.tsx
│       │   └── TypingRaceGame.tsx
│       ├── i18n/index.ts        Localization strings
│       ├── screens/
│       │   ├── LoginScreen.tsx
│       │   ├── RegisterScreen.tsx
│       │   ├── HomeScreen.tsx
│       │   ├── GameScreen.tsx
│       │   ├── ProgressScreen.tsx
│       │   ├── ReportScreen.tsx
│       │   └── ExercisesScreen.tsx
│       ├── services/api.ts      REST client + SecureStore JWT
│       └── utils/eventLogger.ts Tap/keystroke event capture
│
├── ml/                          Offline ML training
│   ├── train.py                 Synthetic data + RandomForest training
│   ├── inference.py             Standalone inference test script
│   ├── requirements.txt         numpy, pandas, scikit-learn, joblib
│   └── models/
│       ├── .gitkeep
│       └── risk_classifier.joblib   (generated locally, gitignored)
│
└── docs/                        Documentation
    ├── README.md                Documentation index
    ├── technical-system-documentation.md   (this document)
    ├── deployment-and-run.md    Setup & troubleshooting
    ├── api-contract.md          REST API schemas
    ├── database-schema.md       ER diagram & table specs
    ├── feature-matrix.md        Biomarker definitions
    ├── literature-review.md     Research background
    ├── phase5-testing.md        Test scenarios
    └── simulation-flow.json     Machine-readable API sequence
```

---

## 7. Technology Stack & Version Matrix

### Backend

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 3.0.3 | Web framework |
| Flask-SQLAlchemy | 3.1.1 | ORM integration |
| Flask-Migrate | 4.0.7 | Schema migrations (wired, no migrations yet) |
| Flask-JWT-Extended | 4.6.0 | JWT authentication |
| Flask-CORS | 4.0.1 | Cross-origin API access |
| psycopg2-binary | ≥2.9.10 | PostgreSQL driver |
| python-dotenv | 1.0.1 | Environment loading |
| Werkzeug | 3.0.3 | Password hashing |
| reportlab | 4.2.0 | PDF generation |
| numpy | ≥2.1.0 | Numerical arrays |
| pandas | ≥2.2.3 | Feature engineering |
| scikit-learn | ≥1.5.2 | Random Forest classifier |
| joblib | 1.4.2 | Model serialization |
| gunicorn | 22.0.0 | Production WSGI server |

### Mobile

| Package | Version | Purpose |
|---------|---------|---------|
| expo | ^56.0.0 | Expo SDK |
| react | 19.2.3 | UI library |
| react-native | 0.85.3 | Native runtime |
| babel-preset-expo | ~56.0.0 | Metro/Babel transpilation (**required direct dep**) |
| expo-haptics | ~56.0.3 | Haptic feedback in games |
| expo-secure-store | ~56.0.4 | Encrypted JWT storage |
| expo-splash-screen | ~56.0.10 | Splash screen config plugin |
| expo-status-bar | ~56.0.4 | Status bar styling |
| @react-navigation/native | ^6.1.18 | Navigation (installed, manual routing used) |
| react-native-safe-area-context | ~5.7.0 | Safe area insets |
| react-native-screens | 4.25.2 | Native screen containers |
| typescript | ~6.0.3 | Type checking |

### Infrastructure

| Component | Version |
|-----------|---------|
| PostgreSQL | 16-alpine (Docker) |
| Python (backend) | 3.11+ (3.13 supported) |
| Node.js | 18+ |
| Docker Compose | v2 |

### ML

| Package | Purpose |
|---------|---------|
| numpy, pandas | Data generation & manipulation |
| scikit-learn | RandomForestClassifier |
| joblib | Model persistence |

---

# Part III — Database System

## 8. Database Overview & Docker Setup

PostgreSQL runs as a **Docker container** defined in `docker-compose.yml`.

### Docker service: `db`

| Setting | Value |
|---------|-------|
| Image | `postgres:16-alpine` |
| Container name | Derived from project (`nipun-db-1` etc.) |
| Host port | **15432** → container **5432** |
| Database | `pdapp_db` |
| User | `pdapp` |
| Password | `pdapp_secret` |
| Volume | `pgdata:/var/lib/postgresql/data` (persistent) |
| Health check | `pg_isready -U pdapp -d pdapp_db` every 5s |

### Why port 15432?

Many Windows machines run local PostgreSQL on ports 5432 or 5433. Using **15432** avoids port conflicts. Always connect via `127.0.0.1:15432`, not `localhost` (can resolve to IPv6 and fail on some systems).

### Start database

```powershell
docker compose up -d db
docker compose ps          # wait until db shows "healthy"
```

### Docker service: `backend` (optional full stack)

| Setting | Value |
|---------|-------|
| Build | `./backend` Dockerfile |
| Host port | 5000 |
| DATABASE_URL | `postgresql://pdapp:pdapp_secret@db:5432/pdapp_db` |
| ML_MODEL_PATH | `/app/ml_models/risk_classifier.joblib` |
| Volumes | `./backend:/app`, `./ml/models:/app/ml_models` |
| Depends on | `db` (healthy) |
| CMD | `gunicorn --bind 0.0.0.0:5000 --reload run:app` |

---

## 9. Connection Strings & Configuration

Configuration is loaded in `backend/app/config.py`:

```python
_root_env = Path(__file__).resolve().parents[2] / ".env"  # project root first
load_dotenv(_root_env)
load_dotenv()  # cwd fallback

SQLALCHEMY_DATABASE_URI = os.getenv(
    "DATABASE_URL", "postgresql://pdapp:pdapp_secret@127.0.0.1:15432/pdapp_db"
)
ML_MODEL_PATH = os.getenv("ML_MODEL_PATH", "../ml/models/risk_classifier.joblib")
JWT_ACCESS_TOKEN_EXPIRES = 86400 * 7  # 7 days
```

| Deployment | DATABASE_URL |
|------------|--------------|
| Local dev (Flask on host) | `postgresql://pdapp:pdapp_secret@127.0.0.1:15432/pdapp_db` |
| Docker backend container | `postgresql://pdapp:pdapp_secret@db:5432/pdapp_db` |
| Production (managed DB) | Provider-specific connection string |

**Driver:** `psycopg2-binary` via Flask-SQLAlchemy. All queries use ORM — no raw SQL in application code.

---

## 10. Schema Initialization

There are **no `.sql` files** and **no Alembic migration files** in the repository. Schema is defined entirely through SQLAlchemy models.

```powershell
cd backend
python init_db.py
```

This executes:

```python
with app.app_context():
    db.create_all()
```

Flask-Migrate is installed (`Migrate(app, db)`) for future schema evolution, but currently schema changes require model updates and re-initialization on fresh databases.

**No seed data** — the database starts empty. Users and sessions come from mobile registration and gameplay.

---

## 11. Entity-Relationship Model

```
                    ┌─────────────┐
                    │    users    │
                    └──────┬──────┘
           ┌───────────────┼───────────────┬──────────────┐
           │               │               │              │
           ▼               ▼               ▼              ▼
    ┌────────────┐  ┌─────────────┐  ┌──────────────┐  ┌─────────┐
    │ game_logs  │  │ai_predictions│  │exercise_plans│  │ reports │
    └─────┬──────┘  └─────────────┘  └──────────────┘  └─────────┘
          │
          ▼
    ┌────────────┐
    │ biomarkers │
    └────────────┘
```

**Cardinality:**
- `users` 1 → N `game_logs` 1 → N `biomarkers`
- `users` 1 → N `ai_predictions`
- `users` 1 → N `reports`
- `users` 1 → N `exercise_plans` (schema exists; API does not write to it yet)

---

## 12. Table Specifications

### `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | String(36) | PK, UUID | User identifier |
| `email` | String(255) | UNIQUE, NOT NULL, indexed | Login email |
| `password_hash` | String(255) | NOT NULL | Werkzeug hashed password |
| `full_name` | String(255) | NOT NULL | Display name |
| `age` | Integer | NOT NULL | User age |
| `handedness` | String(20) | default `"right"` | left/right/ambidextrous |
| `language_pref` | String(10) | default `"en"` | en/si/mixed |
| `created_at` | DateTime UTC | auto | Registration timestamp |
| `updated_at` | DateTime UTC | auto | Last update |

### `game_logs`

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID PK | Session ID |
| `user_id` | FK → users | Owner |
| `game_type` | String(30) | `bubble_pop`, `piano_tiles`, `typing_race` |
| `device_orientation` | String(20) | portrait/landscape |
| `time_of_day` | String(20) | morning/afternoon/evening/night |
| `score` | Integer | Game score |
| `duration_ms` | Integer | Session length |
| `raw_events` | JSON | **Full tap/keystroke audit trail** |
| `started_at` | DateTime | Session start |
| `completed_at` | DateTime | Session end |

### `biomarkers`

One row per extracted metric event (multiple rows per session).

| Column | Type | Games | Description |
|--------|------|-------|-------------|
| `reaction_time_ms` | Float | Bubble Pop | Stimulus → tap latency |
| `flight_time_ms` | Float | Piano Tiles, Typing Race | Inter-tap/keystroke interval |
| `hold_time_ms` | Float | Typing Race | Key press duration |
| `hand_side` | String(20) | All | left/right/center |
| `asymmetry_ratio` | Float | All | left_mean / right_mean |
| `accuracy_pct` | Float | All | Per-event accuracy |
| `variance_ms` | Float | All | Side-specific timing variance |

### `ai_predictions`

| Column | Type | Description |
|--------|------|-------------|
| `risk_profile` | String(20) | baseline/monitor/elevated/referral |
| `confidence` | Float | Model probability 0–1 |
| `feature_vector` | JSON | 13-feature snapshot |
| `model_version` | String(50) | Default `"1.0.0"` |
| `predicted_at` | DateTime | Analysis timestamp |

### `reports`

| Column | Type | Description |
|--------|------|-------------|
| `pdf_path` | String(500) | Filesystem path to PDF |
| `summary` | JSON | risk_profile, confidence |
| `generated_at` | DateTime | Report timestamp |

### `exercise_plans`

Schema defined but **not populated by API**. Recommendations served from in-memory catalog.

---

## 13. How the Database Links to Each Component

| Component | Read | Write | Tables |
|-----------|------|-------|--------|
| Auth (`/auth/*`) | — | INSERT | `users` |
| Game ingest (`POST /games/sessions`) | — | INSERT | `game_logs`, `biomarkers` |
| Progress (`GET /games/progress`) | SELECT | — | `game_logs`, `biomarkers` |
| Feature engineering | SELECT | — | `game_logs`, `biomarkers` (60-day window) |
| ML analyze (`POST /predictions/analyze`) | SELECT | INSERT | reads logs; writes `ai_predictions` |
| Reports (`POST /reports/generate`) | SELECT | INSERT | reads user/logs; writes `reports` |
| Exercises (`GET /exercises/recommended`) | SELECT | — | `ai_predictions` (latest) |

**Design principle:** Raw events are always preserved in `game_logs.raw_events` JSON, enabling reprocessing if biomarker extraction logic changes.

---

# Part IV — Backend API

## 14. Backend Application Structure

```
backend/app/__init__.py     → create_app() factory
backend/run.py              → if __name__ == "__main__": app.run(host="0.0.0.0", port=5000)
```

**Blueprints registered:**

| Blueprint | Prefix | File |
|-----------|--------|------|
| `auth_bp` | `/api/v1/auth` | routes.py |
| `games_bp` | `/api/v1/games` | routes.py |
| `predictions_bp` | `/api/v1/predictions` | routes.py |
| `reports_bp` | `/api/v1/reports` | routes.py |
| `exercises_bp` | `/api/v1/exercises` | routes.py |

**Global routes:**
- `GET /api/v1/health` → `{ "status": "ok", "service": "motor-dss-backend" }`

**CORS:** All origins allowed on `/api/*` (development configuration).

---

## 15. Authentication & Security Model

| Aspect | Implementation |
|--------|----------------|
| Protocol | JWT Bearer tokens |
| Library | Flask-JWT-Extended |
| Token storage (mobile) | Expo SecureStore (encrypted) |
| Password hashing | Werkzeug `generate_password_hash` |
| Token expiry | 7 days |
| Identity claim | `user.id` (UUID string) |
| Protected routes | `@jwt_required()` decorator |

### Auth flow

```
POST /auth/register or /auth/login
    → Validate credentials / create user
    → create_access_token(identity=user.id)
    → Return { user, access_token }

Subsequent requests:
    Authorization: Bearer <access_token>
    → get_jwt_identity() returns user.id
```

### Security notes for production

- Change `SECRET_KEY` and `JWT_SECRET_KEY` from defaults
- Use HTTPS via reverse proxy
- Never expose PostgreSQL publicly
- Add rate limiting at proxy layer
- Set `FLASK_ENV=production`, disable debug mode

---

## 16. REST API Reference

Base URL: `/api/v1`

### Health

| Method | Path | Auth | Response |
|--------|------|------|----------|
| GET | `/health` | No | `{ "status": "ok", "service": "motor-dss-backend" }` |

### Authentication

**POST `/auth/register`**

Request:
```json
{
  "email": "user@example.com",
  "password": "securepass",
  "full_name": "Patient Name",
  "age": 68,
  "handedness": "right",
  "language_pref": "en"
}
```

Response `201`: `{ "user": {...}, "access_token": "..." }`

**POST `/auth/login`**

Request: `{ "email": "...", "password": "..." }`  
Response `200`: `{ "user": {...}, "access_token": "..." }`

### Games

**POST `/games/sessions`**

Request:
```json
{
  "game_type": "bubble_pop",
  "device_orientation": "portrait",
  "time_of_day": "morning",
  "score": 450,
  "duration_ms": 30000,
  "raw_events": [
    {
      "type": "tap",
      "x": 100, "y": 400,
      "hand_side": "left",
      "timestamp_ms": 1000,
      "reaction_time_ms": 380,
      "hit": true
    }
  ],
  "started_at": "2026-06-27T08:00:00Z",
  "completed_at": "2026-06-27T08:00:30Z"
}
```

Response `201`: `{ "session_id": "uuid", "biomarkers": [...] }`

**GET `/games/sessions`** — Query: `?game_type=bubble_pop&limit=30&offset=0`  
Response `200`: `{ "sessions": [...], "total": N }`

**GET `/games/progress`**

Response `200`:
```json
{
  "total_sessions": 45,
  "streak_days": 7,
  "avg_reaction_time_ms": 380.2,
  "avg_flight_time_ms": 210.5,
  "asymmetry_trend": -0.02,
  "recent_scores": [...]
}
```

### Predictions

**POST `/predictions/analyze`**

Response `200`:
```json
{
  "risk_profile": "monitor",
  "confidence": 0.72,
  "feature_summary": {
    "rt_rolling_mean_7d": 385.1,
    "ft_asymmetry_trend": 0.04,
    "sustained_asymmetry_flag": 0
  },
  "recommendation": "Mild asymmetry trend detected. Continue daily assessments and track progress."
}
```

**GET `/predictions/history`** — Response: `{ "predictions": [...] }` (last 20)

### Reports

**POST `/reports/generate`** — Response `201`: `{ "report_id": "uuid", "download_url": "/api/v1/reports/{id}/download" }`

**GET `/reports/{id}/download`** — Response: `application/pdf` file stream

### Exercises

**GET `/exercises/recommended`**

Response `200`:
```json
{
  "exercises": [
    {
      "key": "finger_tap",
      "title_en": "Finger Tapping Exercise",
      "title_si": "ඇඟිලි තට්ටු ව්‍යායාම",
      "instructions_en": "...",
      "instructions_si": "..."
    }
  ]
}
```

### Error format

```json
{
  "error": "validation_error",
  "message": "email is required",
  "details": {}
}
```

HTTP codes: 400, 401, 404, 409, 500

Full schemas: [API Contract](./api-contract.md)

---

## 17. Biomarker Extraction Service

**File:** `backend/app/services/biomarker_service.py`

Entry point: `extract_biomarkers(game_type, raw_events)`

### Bubble Pop (`bubble_pop`)

- Extracts `reaction_time_ms` per tap
- Hand side from event or inferred from screen X coordinate
- Computes session-level `asymmetry_ratio = mean(left RT) / mean(right RT)`
- Per-event `accuracy_pct` from `hit` boolean

### Piano Tiles (`piano_tiles`)

- Extracts `flight_time_ms` (inter-tap interval)
- Computes flight time from consecutive `timestamp_ms` if not provided
- Asymmetry on flight times by hand side

### Typing Race (`typing_race`)

- Extracts `hold_time_ms` (key down → key up)
- Extracts `flight_time_ms` (inter-keystroke interval)
- Hand side from QWERTY key mapping
- Asymmetry on hold times

### Asymmetry formula

```
asymmetry_ratio = round(mean(left_values) / mean(right_values), 4)
```

Defaults to `1.0` if either side has no data or right mean is zero.

---

## 18. Feature Engineering Pipeline

**File:** `backend/app/services/feature_engineering.py`

Function: `build_feature_vector(user_id)` — queries last **60 days** of `game_logs` + `biomarkers`.

| Feature | Computation |
|---------|-------------|
| `rt_rolling_mean_7d` | Mean RT where `started_at >= now - 7 days` |
| `rt_rolling_std_7d` | Std RT in 7-day window |
| `ft_mean`, `ft_std` | Mean/std of all flight times in 60-day window |
| `ht_mean`, `ht_std` | Mean/std of all hold times |
| `ft_asymmetry_trend` | `np.polyfit` slope of asymmetry_ratio over time (≥3 points) |
| `ht_asymmetry_trend` | Copied from `ft_asymmetry_trend` |
| `session_consistency` | `std(scores) / mean(scores)` across sessions |
| `sustained_asymmetry_flag` | 1 if ≥5 of last 14 days have \|asymmetry - 1.0\| > 0.15 |
| `performance_degradation_rate` | Linear slope of session scores |
| `total_sessions` | Count of game_logs in window |
| `accuracy_mean` | Mean accuracy_pct across all biomarkers |

**Empty history:** Returns neutral defaults via `_empty_features()` (RT mean 400, accuracy 100, etc.).

---

## 19. PDF Report Generation

**File:** `backend/app/services/report_service.py`  
**Library:** ReportLab  
**Output:** `backend/app/reports/report_{user_id}_{YYYYMMDD_HHMMSS}.pdf`

### Report sections

1. Title + clinical disclaimer (red text)
2. Patient information table (name, age, handedness, date)
3. Risk assessment summary (profile, confidence, recommendation)
4. Feature summary table (all 13 ML features)
5. Session summary (total sessions, date range)

---

## 20. Exercise Recommendation System

**File:** `backend/app/services/exercise_service.py`

Static bilingual catalog (`EXERCISE_CATALOG`):

| Key | English | Sinhala |
|-----|---------|---------|
| `finger_tap` | Finger Tapping Exercise | ඇඟිලි තට්ටු ව්‍යායාම |
| `squeeze_ball` | Squeeze Ball Exercise | බෝලය තද කිරීමේ ව්‍යායාම |
| `target_touch` | Target Touch Exercise | ඉලක්ක තට්ටු ව්‍යායාම |

**Selection by risk profile:**

| Risk | Exercises returned |
|------|-------------------|
| `baseline` | 1 (finger_tap) |
| `monitor` | 2 (finger_tap, squeeze_ball) |
| `elevated`, `referral` | 3 (all) |

Reads latest `ai_predictions.risk_profile` for the user. Defaults to `baseline` if no prediction exists.

---

# Part V — Mobile Application

## 21. Mobile Stack & Configuration

| Item | Value |
|------|-------|
| Framework | React Native 0.85.3 |
| Expo SDK | **56** (upgraded from SDK 51) |
| React | 19.2.3 |
| Language | TypeScript 6.0 |
| Entry | `expo/AppEntry.js` → `App.tsx` |
| Bundle ID | `com.pdmotor.dss` |
| App name | Motor DSS |
| Orientation | Portrait |
| Splash | `#1a5276` via `expo-splash-screen` plugin |

### Key config files

| File | Purpose |
|------|---------|
| `app.json` | Expo manifest, splash plugin, bundle IDs |
| `babel.config.js` | `babel-preset-expo` preset |
| `tsconfig.json` | Extends `expo/tsconfig.base` |
| `expo-env.d.ts` | Expo TypeScript type reference |
| `.env` | `EXPO_PUBLIC_API_URL` |

---

## 22. Screen Map & User Flow

```
App.tsx (screen state machine)
    │
    ├── login        → LoginScreen
    ├── register     → RegisterScreen
    ├── home         → HomeScreen (game selection, navigation)
    ├── game         → GameScreen → BubblePop / PianoTiles / TypingRace
    ├── progress     → ProgressScreen (dashboard, analyze button)
    ├── exercises    → ExercisesScreen (recommended exercises)
    └── report       → ReportScreen (generate PDF, view results)
```

### First-time user flow

1. Register (name, email, password, age)
2. Read clinical disclaimer banner
3. Play assessment games from HomeScreen
4. View Progress → Run Analysis
5. Generate PDF report for neurologist
6. View recommended exercises

**Auto-login:** On app start, checks SecureStore for existing JWT → navigates to home if found.

---

## 23. Assessment Games

| Game | File | Primary biomarkers | Mechanism |
|------|------|-------------------|-----------|
| Bubble Pop | `BubblePopGame.tsx` | Reaction Time | Tap bubbles; RT = stimulus → tap |
| Piano Tiles | `PianoTilesGame.tsx` | Flight Time | Tap falling tiles on rhythm |
| Typing Race | `TypingRaceGame.tsx` | Hold Time, Flight Time | Type prompted characters |

All games use `expo-haptics` for tactile feedback.

### Hand-side detection

| Game | Method |
|------|--------|
| Bubble Pop / Piano Tiles | Screen divided into thirds by X coordinate |
| Typing Race | QWERTY mapping: left keys (Q–T, A–G, Z–B) vs right keys (Y–P, H–L, N–M) |

---

## 24. Event Capture & Raw Event Schema

**File:** `mobile/src/utils/eventLogger.ts`

```typescript
type TapEvent = {
  type: 'tap' | 'key';
  x?: number;
  y?: number;
  key?: string;
  hand_side: 'left' | 'right' | 'center';
  timestamp_ms: number;        // performance.now()
  reaction_time_ms?: number;
  flight_time_ms?: number;     // ts - lastTimestamp
  hold_time_ms?: number;       // keyup - keydown
  hit?: boolean;
  on_time?: boolean;
  correct?: boolean;
};
```

Events are submitted as `raw_events[]` in the session POST payload. The backend preserves them verbatim in `game_logs.raw_events`.

---

## 25. Mobile API Client

**File:** `mobile/src/services/api.ts`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `register()` | POST `/auth/register` | Create account, store JWT |
| `login()` | POST `/auth/login` | Authenticate, store JWT |
| `logout()` | — | Delete JWT from SecureStore |
| `submitSession()` | POST `/games/sessions` | Submit game results |
| `getProgress()` | GET `/games/progress` | Dashboard data |
| `analyze()` | POST `/predictions/analyze` | Run ML analysis |
| `generateReport()` | POST `/reports/generate` | Create PDF |
| `getExercises()` | GET `/exercises/recommended` | Get exercises |

**Base URL:** `process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:5000/api/v1'`

**Physical device requirement:** Must use PC LAN IP, not `localhost`.

---

## 26. Expo SDK 56 Upgrade Notes

The project was upgraded from **Expo SDK 51 → SDK 56** to match current Expo Go on app stores.

### Version changes

| Package | SDK 51 | SDK 56 |
|---------|--------|--------|
| expo | ~51.0.28 | ^56.0.0 |
| react | 18.2.0 | 19.2.3 |
| react-native | 0.74.5 | 0.85.3 |
| expo-haptics | ~13.0.1 | ~56.0.3 |
| expo-secure-store | ~13.0.2 | ~56.0.4 |

### Removed packages

- `expo-av` — removed (deprecated in SDK 55+; was unused in codebase)

### Added packages

- `babel-preset-expo` — **must be a direct dependency** (see troubleshooting)
- `expo-splash-screen` — replaces deprecated `splash` key in app.json

### Config changes

- `app.json`: removed top-level `splash`; added `expo-splash-screen` plugin
- `tsconfig.json`: extends `expo/tsconfig.base` (removed manual `moduleResolution: "node"`)
- Added `expo-env.d.ts` for TypeScript `process.env` support

### New Architecture

SDK 56 requires React Native **New Architecture** (enabled by default). Legacy architecture is not supported.

---

# Part VI — Machine Learning

## 27. ML Pipeline Overview

```
TRAINING (offline)                          INFERENCE (runtime)
─────────────────                          ──────────────────
ml/train.py                                backend/ml_service.py
    │                                          │
    ▼                                          ▼
generate_synthetic_data(2000)              build_feature_vector(user_id)
    │                                          │ (reads PostgreSQL)
    ▼                                          ▼
RandomForestClassifier.fit()               model.predict_proba()
    │                                          │
    ▼                                          ▼
risk_classifier.joblib                     risk_profile + confidence
```

---

## 28. Training Dataset (Synthetic)

### Critical finding: no real patient data

| Property | Value |
|----------|-------|
| **Data source** | Programmatic generation in `ml/train.py` |
| **External files** | **None** — no CSV, JSON, or clinical database |
| **Sample count** | 2,000 rows |
| **Random seed** | 42 |
| **Public datasets used** | **None** (not PPMI, mPower, or similar) |
| **Purpose** | Academic proxy for model validation |

There is **no real clinical dataset**. The synthetic data simulates longitudinal motor profiles informed by PD asymmetry literature (see [Literature Review](./literature-review.md)).

### Class distribution

| Risk profile | Probability | Simulated motor pattern |
|--------------|-------------|------------------------|
| `baseline` | 50% | RT ~380±30 ms, asymmetry trend ~0, no sustained flag |
| `monitor` | 25% | RT ~400±35 ms, trend ~0.02, 30% sustained flag |
| `elevated` | 15% | RT ~430±40 ms, trend ~0.04, 70% sustained flag |
| `referral` | 10% | RT ~470±50 ms, trend ~0.06, always sustained, negative score slope |

### Synthetic generation logic (excerpt)

```python
for _ in range(n_samples):
    profile = rng.choice(RISK_LABELS, p=[0.50, 0.25, 0.15, 0.10])
    if profile == "referral":
        rt_mean = rng.normal(470, 50)
        asym_trend = rng.normal(0.06, 0.02)
        sustained = 1
        degradation = rng.normal(-5, 2)
    # ... append row with all 13 features + risk_profile label
```

Each row draws FT, HT, session count, accuracy, etc. from profile-specific Gaussian distributions.

---

## 29. Feature Vector Specification

13 features — **identical column order** in training and inference:

| # | Feature | Training source | Inference source |
|---|---------|----------------|------------------|
| 1 | `rt_rolling_mean_7d` | Synthetic Gaussian | 7-day mean from DB |
| 2 | `rt_rolling_std_7d` | Synthetic Gaussian | 7-day std from DB |
| 3 | `ft_mean` | Synthetic Gaussian | 60-day mean flight time |
| 4 | `ft_std` | Synthetic Gaussian | 60-day std flight time |
| 5 | `ht_mean` | Synthetic Gaussian | 60-day mean hold time |
| 6 | `ht_std` | Synthetic Gaussian | 60-day std hold time |
| 7 | `ft_asymmetry_trend` | Profile-specific | polyfit slope |
| 8 | `ht_asymmetry_trend` | FT trend + noise | Copied from FT trend |
| 9 | `session_consistency` | Synthetic Gaussian | std/mean of scores |
| 10 | `sustained_asymmetry_flag` | Profile-specific 0/1 | 14-day threshold logic |
| 11 | `performance_degradation_rate` | Profile-specific | Score slope |
| 12 | `total_sessions` | Random 5–59 | Count in 60-day window |
| 13 | `accuracy_mean` | Synthetic 60–100 | Mean accuracy from DB |

Full biomarker definitions: [Feature Matrix](./feature-matrix.md)

---

## 30. Model Architecture & Hyperparameters

| Parameter | Value |
|-----------|-------|
| Algorithm | `sklearn.ensemble.RandomForestClassifier` |
| Type | Ensemble of decision trees (not neural network) |
| `n_estimators` | 200 |
| `max_depth` | 10 |
| `min_samples_leaf` | 5 |
| `random_state` | 42 |
| `class_weight` | `"balanced"` |
| Train/test split | 80/20 stratified |
| Test accuracy | ~89% on synthetic holdout |

**Output classes:** `[baseline, monitor, elevated, referral]` (ordinal risk tiers)

**Prediction method:** `predict_proba()` → argmax → map index to label

---

## 31. Training Procedure

```powershell
cd ml
pip install -r requirements.txt
python train.py
```

Steps executed by `train_model()`:

1. `df = generate_synthetic_data()` — 2000 rows in memory
2. Split X (13 features) and y (`risk_profile`)
3. `LabelEncoder.fit(["baseline", "monitor", "elevated", "referral"])`
4. Stratified 80/20 split, seed 42
5. Fit RandomForestClassifier
6. Print classification report
7. Save joblib bundle to `ml/models/risk_classifier.joblib`

**Standalone test:**

```powershell
python inference.py
python inference.py models/risk_classifier.joblib
```

---

## 32. Model Artifact Format

**Path:** `ml/models/risk_classifier.joblib`  
**Git status:** Gitignored — must be generated locally

```python
{
    "model": RandomForestClassifier,      # fitted sklearn model
    "label_encoder": LabelEncoder,        # saved but not used at inference
    "features": FEATURE_COLUMNS           # list of 13 feature names
}
```

| Context | ML_MODEL_PATH |
|---------|---------------|
| Local dev | `../ml/models/risk_classifier.joblib` |
| Docker | `/app/ml_models/risk_classifier.joblib` |
| Override | `ML_MODEL_PATH` in `.env` |

---

## 33. Inference Engine & Rule-Based Fallback

**File:** `backend/app/services/ml_service.py`  
**Class:** `MLInferenceEngine`

### ML path (model file exists)

```python
features = build_feature_vector(user_id)
vector = np.array([[features[k] for k in FEATURE_ORDER]])
proba = model.predict_proba(vector)[0]
risk_profile = RISK_LABELS[argmax(proba)]
confidence = proba[argmax_index]
```

### Rule-based fallback (model file missing)

| Condition | Score |
|-----------|-------|
| \|ft_asymmetry_trend\| > 0.02 | +1 |
| sustained_asymmetry_flag == 1 | +2 |
| performance_degradation_rate < -2 | +1 |
| rt_rolling_std_7d > 50 | +1 |

| Total score | Profile | Confidence |
|-------------|---------|------------|
| ≥ 4 | referral | 0.75 |
| ≥ 3 | elevated | 0.70 |
| ≥ 1 | monitor | 0.65 |
| 0 | baseline | 0.80 |

The backend **automatically falls back** if `risk_classifier.joblib` is absent.

---

## 34. Risk Tiers & Clinical Recommendations

| Profile | Meaning (decision support) | Recommendation text |
|---------|---------------------------|---------------------|
| `baseline` | No sustained asymmetry | Continue regular assessments |
| `monitor` | Mild asymmetry trend | Continue daily assessments, track progress |
| `elevated` | Sustained asymmetric patterns | Consult neurologist |
| `referral` | Progressive degradation | Immediate neurologist consultation |

Recommendations are hardcoded in `ml_service.py` `RECOMMENDATIONS` dict and embedded in PDF reports.

---

## 35. Train vs Inference Data Gap

| Aspect | Training | Inference |
|--------|----------|-----------|
| Data | Synthetic Gaussian profiles | Real PostgreSQL biomarker history |
| Labels | Co-generated with features | Predicted by model |
| Feature logic | Direct random draws | Rolling windows, polyfit, threshold flags |
| Validation | ~89% on synthetic test set | Not clinically validated |

**The model has not been retrained on exported real user data.** This is a documented academic limitation.

---

# Part VII — Operations

## 36. Complete Setup Guide (A–Z)

### Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Docker Desktop | Latest | Must be running |
| Python | 3.11+ | 3.13 supported |
| Node.js | 18+ | For mobile |
| npm | 9+ | For mobile |
| Expo Go | SDK 56 | On physical phone for testing |

### Step A — Clone & environment files

```powershell
cd <project-root>
copy .env.example .env
cd mobile
copy .env.example .env
```

### Step B — Start Docker PostgreSQL

```powershell
cd <project-root>
docker compose up -d db
docker compose ps    # wait for "healthy"
```

### Step C — Initialize backend

```powershell
cd backend
pip install -r requirements.txt
python init_db.py
```

### Step D — Train ML model (first time)

```powershell
cd ml
pip install -r requirements.txt
python train.py
```

Confirm: `ml/models/risk_classifier.joblib` exists.

### Step E — Start backend

```powershell
cd backend
python run.py
```

Verify: `Invoke-RestMethod http://127.0.0.1:5000/api/v1/health`

### Step F — Configure mobile

Edit `mobile/.env`:

```
EXPO_PUBLIC_API_URL=http://<YOUR_PC_LAN_IP>:5000/api/v1
```

Find IP: `ipconfig` → Wi-Fi IPv4 address.

### Step G — Start mobile

```powershell
cd mobile
npm install
npx expo start --lan -c
```

Scan QR code with Expo Go on phone (same Wi-Fi).

### Step H — Windows Firewall (one-time, Admin)

```powershell
New-NetFirewallRule -DisplayName "Motor DSS Flask" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

---

## 37. Environment Variables Reference

### Root `.env` (backend)

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://pdapp:pdapp_secret@127.0.0.1:15432/pdapp_db` | PostgreSQL connection |
| `FLASK_APP` | `app` | Flask entry |
| `FLASK_ENV` | `development` | Set `production` in prod |
| `SECRET_KEY` | (change me) | Flask secret |
| `JWT_SECRET_KEY` | (change me) | JWT signing |
| `ML_MODEL_PATH` | `../ml/models/risk_classifier.joblib` | Trained model |

### Mobile `.env`

| Variable | Example | Description |
|----------|---------|-------------|
| `EXPO_PUBLIC_API_URL` | `http://192.168.1.63:5000/api/v1` | Backend API base |

| Target device | URL |
|---------------|-----|
| Physical phone (same Wi-Fi) | `http://<PC_IP>:5000/api/v1` |
| Android emulator | `http://10.0.2.2:5000/api/v1` |
| iOS simulator | `http://localhost:5000/api/v1` |

---

## 38. Deployment Modes

### Mode A — Local development (recommended)

- Docker: PostgreSQL only
- Backend: `python run.py` on host
- Mobile: `npx expo start --lan -c`
- DB: `127.0.0.1:15432`

### Mode B — Full Docker stack

```powershell
cd ml && python train.py          # train first
cd .. && docker compose up -d --build
docker compose exec backend python init_db.py
```

- Backend: `http://localhost:5000`
- DB: `127.0.0.1:15432`
- ML model mounted from `./ml/models`

### Mode C — Production (research/demo)

```
Mobile (EAS build) → HTTPS → Reverse Proxy → Gunicorn → Managed PostgreSQL
                                                          → ML model volume
```

```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 run:app
```

---

## 39. Verification & Testing

### Health check

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/v1/health
```

### Register test user

```powershell
$body = @{
  email = "test@example.com"
  password = "test12345"
  full_name = "Test User"
  age = 68
} | ConvertTo-Json

Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:5000/api/v1/auth/register" `
  -ContentType "application/json" -Body $body
```

### Submit session & analyze

Use token from registration:

```powershell
# POST /games/sessions (see deployment-and-run.md for full payload)
# POST /predictions/analyze
# POST /reports/generate
```

### Test scenarios

| Scenario | Expected risk | Details |
|----------|---------------|---------|
| Baseline user | `baseline` | Symmetric RT 350–400 ms, asymmetry ~1.0 |
| Monitor user | `monitor` | Gradual asymmetry increase over 21 days |
| Elevated user | `elevated` | 10+ sessions, left RT 15%+ slower |
| Referral user | `referral` | Declining scores + high variance + sustained asymmetry |

Full scenarios: [Phase 5 Testing](./phase5-testing.md)

### Backend checks

```powershell
cd backend && npx expo-doctor    # N/A for backend
cd mobile && npx expo-doctor       # 21/21 checks should pass
cd mobile && npx tsc --noEmit      # TypeScript compile check
```

---

## 40. Troubleshooting Encyclopedia

### Expo Go: "Project incompatible with SDK 56"

**Cause:** Project on SDK 51, Expo Go app is SDK 56.

**Fix:** Project upgraded to SDK 56. Run:

```powershell
cd mobile
npm install
npx expo start --lan -c
```

Alternative: install legacy Expo Go for SDK 51 from [expo.dev/go](https://expo.dev/go?sdkVersion=51&platform=android&device=true).

---

### Metro: `Cannot read properties of undefined (reading 'transformFile')`

**Cause:** Metro transformer failed to initialize. Usually **`babel-preset-expo` not found** as a direct dependency.

**Fix:**

```powershell
cd mobile
npx expo install babel-preset-expo
npx expo start -c
```

Verify `babel-preset-expo` appears in `package.json` dependencies.

**Clean reinstall if needed:**

```powershell
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
npx expo start --lan -c
```

---

### Mobile: `Network request failed`

**Cause:** `EXPO_PUBLIC_API_URL` uses `localhost` (refers to phone, not PC).

**Fix:**
1. `ipconfig` → get PC Wi-Fi IPv4
2. Set `EXPO_PUBLIC_API_URL=http://<IP>:5000/api/v1`
3. Ensure backend running
4. Add Windows Firewall rule for port 5000
5. Restart Expo with `-c` flag

---

### Database: `password authentication failed for user "pdapp"`

**Cause:** Stale Docker volume or wrong port.

**Fix:**

```powershell
docker compose down -v
docker compose up -d db
cd backend && python init_db.py
```

Ensure `.env` uses `127.0.0.1:15432`.

---

### ML: Predictions use rule-based fallback only

**Cause:** Model file missing.

**Fix:**

```powershell
cd ml && python train.py
# Verify ml/models/risk_classifier.joblib exists
# Restart backend
```

---

### Docker: `dockerDesktopLinuxEngine` pipe not found

**Cause:** Docker Desktop not running.

**Fix:** Start Docker Desktop, wait for "Running" status.

---

### npm: `ECONNRESET` or `EPERM` during install

**Fix:**

```powershell
cd mobile
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
npm cache clean --force
npm install --fetch-retries=5
```

Close programs locking `node_modules` if EPERM errors persist.

---

### Python 3.13: package build failures

Use flexible pins in `requirements.txt` (`numpy>=2.1.0`, not pinned to 1.26.x).

---

## 41. Production Deployment Checklist

- [ ] Change `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] HTTPS via reverse proxy (Nginx, Caddy, cloud LB)
- [ ] Never expose PostgreSQL publicly
- [ ] Use managed PostgreSQL (RDS, Supabase, Neon)
- [ ] Set `FLASK_ENV=production`
- [ ] Disable Flask debug mode
- [ ] Gunicorn with multiple workers (no `--reload`)
- [ ] Rate limiting at proxy
- [ ] Train and deploy ML model to accessible path
- [ ] Set `EXPO_PUBLIC_API_URL` in EAS secrets for mobile builds
- [ ] Clinical disclaimer visible in app and PDF reports

---

# Part VIII — Reference

## 42. End-to-End Sequence Flows

### Registration → First game → Analysis

```
1. Mobile: POST /auth/register
   → DB: INSERT users
   → Mobile: SecureStore.setItem('access_token')

2. Mobile: User plays Bubble Pop
   → EventLogger captures taps
   → POST /games/sessions { raw_events, score, ... }
   → DB: INSERT game_logs + biomarkers

3. Mobile: ProgressScreen → "Analyze"
   → POST /predictions/analyze
   → Backend: build_feature_vector → ML predict
   → DB: INSERT ai_predictions
   → Mobile: Display risk profile

4. Mobile: ReportScreen → "Generate Report"
   → POST /reports/generate
   → Backend: PDF via ReportLab
   → DB: INSERT reports
   → Mobile: Show download link
```

### Data lifecycle

```
Raw tap event (mobile)
    → raw_events JSON (PostgreSQL)
    → biomarker rows (PostgreSQL)
    → 13-feature vector (in-memory)
    → risk prediction (PostgreSQL)
    → PDF report (filesystem + PostgreSQL metadata)
```

---

## 43. Known Limitations & Future Work

| Limitation | Detail |
|------------|--------|
| Synthetic training data | No real patient/clinical dataset |
| No clinical validation | Not validated against neurological diagnosis |
| Train/inference gap | Different feature generation logic |
| No Alembic migrations | Schema via ORM `create_all()` only |
| `exercise_plans` unused | Recommendations from in-memory catalog |
| Model not in git | Must train locally |
| Doc/schema gaps | Docs describe DB ENUMs not enforced in ORM |
| Research prototype | Not for clinical use without regulatory review |

### Future work

- Retrain on real anonymized longitudinal data
- Alembic migrations for schema versioning
- Persist exercise assignments to `exercise_plans`
- EAS production mobile builds
- EHR integration
- Clinical validation study

---

## 44. Glossary

| Term | Definition |
|------|------------|
| **RT** | Reaction Time — stimulus to first response (ms) |
| **FT** | Flight Time — interval between consecutive taps/keys (ms) |
| **HT** | Hold Time — key press duration (ms) |
| **Asymmetry ratio** | Left-side mean ÷ right-side mean (1.0 = symmetric) |
| **Biomarker** | Quantified motor metric extracted from raw events |
| **Digital biomarker** | Device-captured physiological/behavioral indicator |
| **Feature vector** | 13 numeric values fed to ML model |
| **Risk profile** | One of: baseline, monitor, elevated, referral |
| **Longitudinal** | Tracked over multiple sessions/days |
| **Proxy dataset** | Synthetic data approximating real patterns |
| **Decision support** | Information aid — not a diagnosis |
| **JWT** | JSON Web Token for API authentication |
| **ORM** | Object-Relational Mapping (SQLAlchemy) |
| **Expo Go** | Client app for running Expo projects during development |

---

## 45. File Reference Index

| Concern | Primary file(s) |
|---------|-----------------|
| Docker / Postgres | `docker-compose.yml` |
| DB connection | `.env.example`, `backend/app/config.py` |
| Schema / ORM | `backend/app/models.py` |
| DB init | `backend/init_db.py` |
| API routes | `backend/app/routes.py` |
| Auth | `routes.py`, `config.py` |
| Biomarkers | `backend/app/services/biomarker_service.py` |
| Features | `backend/app/services/feature_engineering.py` |
| ML inference | `backend/app/services/ml_service.py` |
| ML training | `ml/train.py` |
| ML test | `ml/inference.py` |
| PDF reports | `backend/app/services/report_service.py` |
| Exercises | `backend/app/services/exercise_service.py` |
| Mobile API | `mobile/src/services/api.ts` |
| Event capture | `mobile/src/utils/eventLogger.ts` |
| Games | `mobile/src/games/*.tsx` |
| Screens | `mobile/src/screens/*.tsx` |
| Expo config | `mobile/app.json`, `mobile/package.json` |

---

## 46. Related Documentation

| Document | Description |
|----------|-------------|
| [Documentation Index](./README.md) | All docs listing |
| [Deployment & Run Guide](./deployment-and-run.md) | Step-by-step setup & troubleshooting |
| [API Contract](./api-contract.md) | REST endpoint schemas |
| [Database Schema](./database-schema.md) | ER diagram & intended constraints |
| [Feature Matrix](./feature-matrix.md) | Biomarker definitions |
| [Literature Review](./literature-review.md) | Research background |
| [Phase 5 Testing](./phase5-testing.md) | Test scenarios & acceptance |
| [Simulation Flow](./simulation-flow.json) | Machine-readable API sequence |

---

*Motor DSS — Academic research project. Not for clinical use without regulatory approval.*

*Document version 2.0 — June 2026*
