"""Create tables and seed the current research/demo dataset.

Usage:
    python init_db.py
    python init_db.py --force-seed   # wipe seeded rows and reload snapshot
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime

from app import create_app
from app.models import AIPrediction, Biomarker, GameLog, Report, User, db

SEED_PATH = os.path.join(os.path.dirname(__file__), "seed_snapshot.json")
DEMO_EMAIL = "sim@example.com"
DEMO_PASSWORD = "sim12345"


def _parse_dt(value):
    if not value:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    # Postgres TIMESTAMP WITHOUT TIME ZONE expects naive UTC.
    if dt.tzinfo is not None:
        from datetime import timezone

        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def load_seed_file():
    if not os.path.exists(SEED_PATH):
        raise FileNotFoundError(f"Seed file not found: {SEED_PATH}")
    with open(SEED_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def clear_seed_data():
    Report.query.delete()
    AIPrediction.query.delete()
    Biomarker.query.delete()
    GameLog.query.delete()
    User.query.delete()
    db.session.commit()


def seed_database(data, *, force=False):
    if User.query.first() and not force:
        print("Database already has users — skipping seed.")
        print(f"Demo login: {DEMO_EMAIL} / {DEMO_PASSWORD}")
        return False

    if force:
        print("Force seed requested — clearing existing rows...")
        clear_seed_data()

    users_by_old_id = {}
    for row in data.get("users", []):
        user = User(
            id=row.get("id"),
            email=row["email"],
            full_name=row["full_name"],
            age=int(row["age"]),
            handedness=row.get("handedness", "right"),
            language_pref=row.get("language_pref", "en"),
            created_at=_parse_dt(row.get("created_at")),
        )
        # Re-hash so seed works across Werkzeug versions.
        user.set_password(DEMO_PASSWORD if row["email"] == DEMO_EMAIL else row.get("password", DEMO_PASSWORD))
        db.session.add(user)
        users_by_old_id[row["id"]] = user

    db.session.flush()

    for row in data.get("game_logs", []):
        log = GameLog(
            id=row.get("id"),
            user_id=row["user_id"],
            game_type=row["game_type"],
            device_orientation=row.get("device_orientation", "portrait"),
            time_of_day=row.get("time_of_day", "morning"),
            score=row.get("score", 0),
            duration_ms=row.get("duration_ms", 0),
            raw_events=row.get("raw_events", []),
            started_at=_parse_dt(row["started_at"]),
            completed_at=_parse_dt(row.get("completed_at")),
        )
        db.session.add(log)
        db.session.flush()
        for bm in row.get("biomarkers", []):
            db.session.add(
                Biomarker(
                    game_log_id=log.id,
                    reaction_time_ms=bm.get("reaction_time_ms"),
                    flight_time_ms=bm.get("flight_time_ms"),
                    hold_time_ms=bm.get("hold_time_ms"),
                    hand_side=bm.get("hand_side"),
                    asymmetry_ratio=bm.get("asymmetry_ratio"),
                    accuracy_pct=bm.get("accuracy_pct"),
                    variance_ms=bm.get("variance_ms"),
                )
            )

    for row in data.get("predictions", []):
        db.session.add(
            AIPrediction(
                user_id=row["user_id"],
                risk_profile=row["risk_profile"],
                confidence=row["confidence"],
                feature_vector=row.get("feature_vector", {}),
                model_version=row.get("model_version", "1.0.0"),
                predicted_at=_parse_dt(row.get("predicted_at")),
            )
        )

    for row in data.get("reports", []):
        pdf_path = row.get("pdf_path")
        if pdf_path and not os.path.exists(pdf_path):
            pdf_path = None
        db.session.add(
            Report(
                user_id=row["user_id"],
                pdf_path=pdf_path,
                summary=row.get("summary", {}),
                generated_at=_parse_dt(row.get("generated_at")),
            )
        )

    db.session.commit()
    counts = data.get("counts") or {
        "users": len(data.get("users", [])),
        "game_logs": len(data.get("game_logs", [])),
        "biomarkers": sum(len(l.get("biomarkers", [])) for l in data.get("game_logs", [])),
        "predictions": len(data.get("predictions", [])),
        "reports": len(data.get("reports", [])),
    }
    print("Seed complete:")
    for key, value in counts.items():
        print(f"  {key}: {value}")
    print(f"Demo login: {DEMO_EMAIL} / {DEMO_PASSWORD}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Create Motor DSS tables and seed demo data.")
    parser.add_argument(
        "--force-seed",
        action="store_true",
        help="Delete existing users/sessions/predictions/reports and reload seed_snapshot.json",
    )
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        db.create_all()
        print("Database tables created.")
        seed = load_seed_file()
        seed_database(seed, force=args.force_seed)


if __name__ == "__main__":
    main()
