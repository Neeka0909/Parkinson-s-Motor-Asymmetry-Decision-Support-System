# REST API Contract — v1

Base URL: `/api/v1`

## Authentication

### POST /auth/register

```json
{
  "email": "user@example.com",
  "password": "securepass",
  "full_name": "Patient Name",
  "age": 68,
  "handedness": "right",
  "language_pref": "mixed"
}
```

**Response 201:** `{ "user": {...}, "access_token": "..." }`

### POST /auth/login

```json
{ "email": "user@example.com", "password": "securepass" }
```

**Response 200:** `{ "user": {...}, "access_token": "..." }`

---

## Games

### POST /games/sessions

Submit a completed game session with raw events.

```json
{
  "game_type": "bubble_pop",
  "device_orientation": "portrait",
  "time_of_day": "morning",
  "score": 42,
  "duration_ms": 60000,
  "raw_events": [
    {
      "type": "tap",
      "x": 120, "y": 400,
      "hand_side": "left",
      "timestamp_ms": 1234567890.123,
      "reaction_time_ms": 342.5
    }
  ],
  "started_at": "2026-06-27T08:00:00Z",
  "completed_at": "2026-06-27T08:01:00Z"
}
```

**Response 201:** `{ "session_id": "uuid", "biomarkers": [...] }`

### GET /games/sessions

Query params: `?game_type=bubble_pop&limit=30&offset=0`

**Response 200:** `{ "sessions": [...], "total": 45 }`

### GET /games/progress

Longitudinal progress summary for dashboard.

**Response 200:**

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

---

## Predictions

### POST /predictions/analyze

Trigger ML analysis on user's longitudinal data.

**Response 200:**

```json
{
  "risk_profile": "monitor",
  "confidence": 0.72,
  "feature_summary": {
    "rt_rolling_mean_7d": 385.1,
    "ft_asymmetry_trend": 0.04,
    "sustained_asymmetry_flag": false
  },
  "recommendation": "Continue regular assessments. Mild left-side variance detected."
}
```

### GET /predictions/history

**Response 200:** `{ "predictions": [...] }`

---

## Reports

### POST /reports/generate

Generate PDF decision-support report for neurologist.

**Response 201:** `{ "report_id": "uuid", "download_url": "/api/v1/reports/{id}/download" }`

### GET /reports/{id}/download

**Response 200:** `application/pdf`

---

## Exercises

### GET /exercises/recommended

Based on latest prediction and asymmetry profile.

**Response 200:**

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

---

## Error Format

```json
{
  "error": "validation_error",
  "message": "Age must be between 50 and 120",
  "details": {}
}
```

HTTP codes: 400, 401, 403, 404, 422, 500
