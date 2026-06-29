# Longitudinal Simulation & Testing Guide — Phase 5

## Overview

Phase 5 validates that **Motor DSS** correctly tracks motor performance over time, detects sustained asymmetry trends, and generates clinician-ready PDF reports.

## Prerequisites

Complete setup per [Deployment & Run Guide](./deployment-and-run.md):

- Docker Postgres on `127.0.0.1:15432`
- Backend running on port `5000`
- ML model trained (`ml/models/risk_classifier.joblib`)
- Mobile app configured with correct `EXPO_PUBLIC_API_URL`

## Test Scenarios

### 1. Baseline User (Healthy Pattern)

Simulate 14 sessions over 14 days with symmetric performance:

```python
reaction_time_ms: 350-400   # both sides
flight_time_ms: 180-220     # both sides
hold_time_ms: 140-160       # both hands
asymmetry_ratio: 0.95-1.05
```

**Expected:** Risk profile = `baseline`, no neurologist prompt.

### 2. Monitor User (Mild Asymmetry)

Simulate gradual left-side slowing over 21 days:

- Week 1: asymmetry_ratio ≈ 1.0
- Week 2: asymmetry_ratio ≈ 1.08
- Week 3: asymmetry_ratio ≈ 1.12

**Expected:** Risk profile = `monitor`, finger-tapping exercise recommended.

### 3. Elevated User (Sustained Asymmetry)

Simulate 10+ sessions with consistent left-side RT 15%+ slower.

**Expected:** Risk profile = `elevated`, neurologist consultation prompt.

### 4. Referral User (Progressive Degradation)

Simulate declining scores + high RT variance + sustained asymmetry over 30 days.

**Expected:** Risk profile = `referral`, PDF report with full biomarker features.

## Running Simulation

### 1. Start stack

```powershell
cd <project-root>
docker compose up -d db
cd backend
python init_db.py
python run.py
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

$r = Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:5000/api/v1/auth/register" `
  -ContentType "application/json" -Body $body

$token = $r.access_token
```

### 3. Submit game session (API)

See [simulation-flow.json](./simulation-flow.json) for a full request template.

### 4. Run analysis

```powershell
Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:5000/api/v1/predictions/analyze" `
  -Headers @{ Authorization = "Bearer $token" }
```

### 5. Generate PDF report

```powershell
Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:5000/api/v1/reports/generate" `
  -Headers @{ Authorization = "Bearer $token" }
```

PDF output: `backend/app/reports/`

### 6. Mobile end-to-end test

1. Set `mobile/.env` to PC LAN IP
2. Register via app → play all 3 games → Progress → Run Analysis → Generate Report
3. Confirm no `Network request failed` errors

## Acceptance Criteria

- [ ] Sub-millisecond event timestamps captured in all 3 games
- [ ] Biomarkers extracted and stored per session
- [ ] Longitudinal features computed from 7/14/30-day windows
- [ ] ML classifier returns 4-tier risk profile with confidence
- [ ] PDF report includes disclaimer, patient info, biomarkers, recommendation
- [ ] Bilingual UI renders (English + Sinhala)
- [ ] Exercise recommendations scale with risk level
- [ ] Rule-based fallback works when ML model is absent
- [ ] Physical phone connects to backend via LAN IP

## Thesis Documentation Checklist

- [Feature matrix](./feature-matrix.md)
- [Database schema](./database-schema.md)
- [API contract](./api-contract.md)
- [Literature review](./literature-review.md)
- [Deployment guide](./deployment-and-run.md)
- ML validation results (`python ml/train.py` classification report)
- Limitations: synthetic data, no clinical validation, decision-support only
