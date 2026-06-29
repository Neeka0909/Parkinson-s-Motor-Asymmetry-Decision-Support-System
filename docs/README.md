# Documentation Index — Motor DSS

| Document | Purpose |
|----------|---------|
| [Deployment & Run Guide](./deployment-and-run.md) | **Start here** — setup, ports, mobile, troubleshooting |
| [API Contract](./api-contract.md) | REST endpoints (`/api/v1`) |
| [Database Schema](./database-schema.md) | PostgreSQL tables & relationships |
| [Feature Matrix](./feature-matrix.md) | Digital biomarkers (RT, FT, HT, asymmetry) |
| [Literature Review](./literature-review.md) | Research background & references |
| [Phase 5 Testing](./phase5-testing.md) | Longitudinal simulation & acceptance criteria |
| [Simulation Flow](./simulation-flow.json) | Sample API request sequence |

## Current Configuration Summary

| Item | Value |
|------|-------|
| Application name | Motor DSS |
| Backend service | `motor-dss-backend` |
| Flask API | `http://0.0.0.0:5000` |
| Docker Postgres | `127.0.0.1:15432` → `pdapp` / `pdapp_db` |
| Mobile (Expo SDK 51) | `com.pdmotor.dss` |
| ML model | `ml/models/risk_classifier.joblib` |
| Mobile API env var | `EXPO_PUBLIC_API_URL` |

See [Deployment & Run Guide](./deployment-and-run.md) for full setup instructions.
