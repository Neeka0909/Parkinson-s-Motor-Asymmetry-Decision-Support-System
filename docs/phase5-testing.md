# Longitudinal Simulation & Testing Guide — Phase 5

## Overview

Phase 5 validates that the system correctly tracks motor performance over time, detects sustained asymmetry trends, and generates clinician-ready PDF reports.

## Test Scenarios

### 1. Baseline User (Healthy Pattern)

Simulate 14 sessions over 14 days with symmetric performance:

```python
# Example session parameters
reaction_time_ms: 350-400 (both sides)
flight_time_ms: 180-220 (both sides)
hold_time_ms: 140-160 (both hands)
asymmetry_ratio: 0.95-1.05
```

**Expected:** Risk profile = `baseline`, no neurologist prompt.

### 2. Monitor User (Mild Asymmetry)

Simulate gradual left-side slowing over 21 days:

- Week 1: asymmetry_ratio ≈ 1.0
- Week 2: asymmetry_ratio ≈ 1.08
- Week 3: asymmetry_ratio ≈ 1.12

**Expected:** Risk profile = `monitor`, exercise recommendations include finger tapping.

### 3. Elevated User (Sustained Asymmetry)

Simulate 10+ sessions with consistent left-side RT 15%+ slower:

**Expected:** Risk profile = `elevated`, mandatory neurologist consultation prompt.

### 4. Referral User (Progressive Degradation)

Simulate declining scores + high RT variance + sustained asymmetry over 30 days.

**Expected:** Risk profile = `referral`, PDF report generated with all biomarker features.

## Running Simulation

```bash
# 1. Start backend
docker compose up -d
cd backend && python init_db.py

# 2. Register test user via API
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@nipun.lk","password":"test123","full_name":"Test User","age":68}'

# 3. Submit game sessions (use mobile app or curl)
# 4. Run analysis
curl -X POST http://localhost:5000/api/v1/predictions/analyze \
  -H "Authorization: Bearer <token>"

# 5. Generate PDF report
curl -X POST http://localhost:5000/api/v1/reports/generate \
  -H "Authorization: Bearer <token>"
```

## Acceptance Criteria

- [ ] Sub-millisecond event timestamps captured in all 3 games
- [ ] Biomarkers extracted and stored per session
- [ ] Longitudinal features computed from 7/14/30-day windows
- [ ] ML classifier returns 4-tier risk profile with confidence
- [ ] PDF report includes disclaimer, patient info, biomarkers, recommendation
- [ ] Bilingual UI renders on mobile (English + Sinhala)
- [ ] Exercise recommendations scale with risk level
- [ ] Rule-based fallback works when ML model is absent

## Thesis Documentation Checklist

- Feature matrix (docs/feature-matrix.md)
- Database schema (docs/database-schema.md)
- API contract (docs/api-contract.md)
- Literature review (docs/literature-review.md)
- Architecture diagram (README.md)
- ML validation results (run ml/train.py, capture classification report)
- Limitations section: synthetic data, no clinical validation, decision-support only
