# Database Schema

## Entity-Relationship Overview

```
Users 1──* GameLogs 1──* Biomarkers
Users 1──* AI_Predictions
Users 1──* Exercise_Plans
Users 1──* Reports
```

## Tables

### users

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| full_name | VARCHAR(255) | NOT NULL |
| age | INTEGER | CHECK 50–120 |
| handedness | ENUM | left, right, ambidextrous |
| language_pref | ENUM | en, si, mixed |
| created_at | TIMESTAMP | DEFAULT NOW() |
| updated_at | TIMESTAMP | |

### game_logs

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| user_id | UUID | FK → users.id |
| game_type | ENUM | bubble_pop, piano_tiles, typing_race |
| device_orientation | ENUM | portrait, landscape |
| time_of_day | ENUM | morning, afternoon, evening, night |
| score | INTEGER | |
| duration_ms | INTEGER | |
| raw_events | JSONB | Sub-ms tap/keystroke events |
| started_at | TIMESTAMP | NOT NULL |
| completed_at | TIMESTAMP | |

### biomarkers

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| game_log_id | UUID | FK → game_logs.id |
| reaction_time_ms | FLOAT | nullable |
| flight_time_ms | FLOAT | nullable |
| hold_time_ms | FLOAT | nullable |
| hand_side | ENUM | left, right, center, bilateral |
| asymmetry_ratio | FLOAT | left/right performance ratio |
| accuracy_pct | FLOAT | 0–100 |
| variance_ms | FLOAT | session variance |

### ai_predictions

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| user_id | UUID | FK → users.id |
| risk_profile | ENUM | baseline, monitor, elevated, referral |
| confidence | FLOAT | 0–1 |
| feature_vector | JSONB | Input features used |
| model_version | VARCHAR(50) | |
| predicted_at | TIMESTAMP | DEFAULT NOW() |

### exercise_plans

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| user_id | UUID | FK → users.id |
| exercise_key | VARCHAR(100) | finger_tap, squeeze_ball, target_touch |
| title_en | VARCHAR(255) | |
| title_si | VARCHAR(255) | |
| instructions_en | TEXT | |
| instructions_si | TEXT | |
| assigned_at | TIMESTAMP | |
| completed_at | TIMESTAMP | nullable |

### reports

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| user_id | UUID | FK → users.id |
| pdf_path | VARCHAR(500) | |
| summary | JSONB | Report metadata |
| generated_at | TIMESTAMP | DEFAULT NOW() |

## Indexes

- `game_logs(user_id, started_at)` — longitudinal queries
- `biomarkers(game_log_id)` — join performance
- `ai_predictions(user_id, predicted_at)` — trend analysis
