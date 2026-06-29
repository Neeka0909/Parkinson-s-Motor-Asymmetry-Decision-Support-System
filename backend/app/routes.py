from datetime import datetime, timezone

from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from app.models import AIPrediction, Biomarker, GameLog, Report, User, db
from app.services.biomarker_service import extract_biomarkers
from app.services.exercise_service import EXERCISE_CATALOG, get_recommended_exercises
from app.services.ml_service import MLInferenceEngine
from app.services.report_service import generate_pdf_report

auth_bp = Blueprint("auth", __name__)
games_bp = Blueprint("games", __name__)
predictions_bp = Blueprint("predictions", __name__)
reports_bp = Blueprint("reports", __name__)
exercises_bp = Blueprint("exercises", __name__)


def _parse_dt(val):
    if isinstance(val, str):
        return datetime.fromisoformat(val.replace("Z", "+00:00"))
    return val


# ── Auth ──────────────────────────────────────────────────────────────────────

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    required = ["email", "password", "full_name", "age"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": "validation_error", "message": f"{field} is required"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "conflict", "message": "Email already registered"}), 409

    user = User(
        email=data["email"],
        full_name=data["full_name"],
        age=int(data["age"]),
        handedness=data.get("handedness", "right"),
        language_pref=data.get("language_pref", "en"),
    )
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=user.id)
    return jsonify({"user": user.to_dict(), "access_token": token}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get("email", "")).first()
    if not user or not user.check_password(data.get("password", "")):
        return jsonify({"error": "unauthorized", "message": "Invalid credentials"}), 401

    token = create_access_token(identity=user.id)
    return jsonify({"user": user.to_dict(), "access_token": token}), 200


# ── Games ─────────────────────────────────────────────────────────────────────

@games_bp.route("/sessions", methods=["POST"])
@jwt_required()
def create_session():
    user_id = get_jwt_identity()
    data = request.get_json()

    log = GameLog(
        user_id=user_id,
        game_type=data["game_type"],
        device_orientation=data.get("device_orientation", "portrait"),
        time_of_day=data.get("time_of_day", "morning"),
        score=data.get("score", 0),
        duration_ms=data.get("duration_ms", 0),
        raw_events=data.get("raw_events", []),
        started_at=_parse_dt(data["started_at"]),
        completed_at=_parse_dt(data.get("completed_at")),
    )
    db.session.add(log)
    db.session.flush()

    biomarker_data = extract_biomarkers(data["game_type"], data.get("raw_events", []))
    biomarkers = []
    for bm in biomarker_data:
        b = Biomarker(game_log_id=log.id, **{k: v for k, v in bm.items() if hasattr(Biomarker, k)})
        db.session.add(b)
        biomarkers.append(b)

    db.session.commit()
    return jsonify({"session_id": log.id, "biomarkers": [b.to_dict() for b in biomarkers]}), 201


@games_bp.route("/sessions", methods=["GET"])
@jwt_required()
def list_sessions():
    user_id = get_jwt_identity()
    game_type = request.args.get("game_type")
    limit = min(int(request.args.get("limit", 30)), 100)
    offset = int(request.args.get("offset", 0))

    q = GameLog.query.filter_by(user_id=user_id)
    if game_type:
        q = q.filter_by(game_type=game_type)

    total = q.count()
    sessions = q.order_by(GameLog.started_at.desc()).offset(offset).limit(limit).all()
    return jsonify({"sessions": [s.to_dict(include_biomarkers=True) for s in sessions], "total": total})


@games_bp.route("/progress", methods=["GET"])
@jwt_required()
def get_progress():
    user_id = get_jwt_identity()
    logs = GameLog.query.filter_by(user_id=user_id).order_by(GameLog.started_at.desc()).all()

    if not logs:
        return jsonify({"total_sessions": 0, "streak_days": 0, "recent_scores": []})

    rts, fts, scores = [], [], []
    for log in logs:
        scores.append({"game_type": log.game_type, "score": log.score, "date": log.started_at.isoformat()})
        for bm in log.biomarkers:
            if bm.reaction_time_ms:
                rts.append(bm.reaction_time_ms)
            if bm.flight_time_ms:
                fts.append(bm.flight_time_ms)

    asymmetry_values = [bm.asymmetry_ratio for log in logs for bm in log.biomarkers if bm.asymmetry_ratio]
    asym_trend = 0.0
    if len(asymmetry_values) >= 2:
        asym_trend = round(asymmetry_values[0] - asymmetry_values[-1], 4)

    return jsonify(
        {
            "total_sessions": len(logs),
            "streak_days": _calc_streak(logs),
            "avg_reaction_time_ms": round(sum(rts) / len(rts), 1) if rts else None,
            "avg_flight_time_ms": round(sum(fts) / len(fts), 1) if fts else None,
            "asymmetry_trend": asym_trend,
            "recent_scores": scores[:10],
        }
    )


def _calc_streak(logs):
    if not logs:
        return 0
    dates = sorted({log.started_at.date() for log in logs}, reverse=True)
    streak = 1
    for i in range(1, len(dates)):
        if (dates[i - 1] - dates[i]).days == 1:
            streak += 1
        else:
            break
    return streak


# ── Predictions ───────────────────────────────────────────────────────────────

@predictions_bp.route("/analyze", methods=["POST"])
@jwt_required()
def analyze():
    user_id = get_jwt_identity()
    engine = MLInferenceEngine()
    result = engine.predict(user_id)

    prediction = AIPrediction(
        user_id=user_id,
        risk_profile=result["risk_profile"],
        confidence=result["confidence"],
        feature_vector=result["feature_summary"],
    )
    db.session.add(prediction)
    db.session.commit()

    return jsonify(result), 200


@predictions_bp.route("/history", methods=["GET"])
@jwt_required()
def prediction_history():
    user_id = get_jwt_identity()
    preds = (
        AIPrediction.query.filter_by(user_id=user_id)
        .order_by(AIPrediction.predicted_at.desc())
        .limit(20)
        .all()
    )
    return jsonify({"predictions": [p.to_dict() for p in preds]})


# ── Reports ───────────────────────────────────────────────────────────────────

@reports_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate_report():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "not_found", "message": "User not found"}), 404

    engine = MLInferenceEngine()
    result = engine.predict(user_id)

    logs = GameLog.query.filter_by(user_id=user_id).order_by(GameLog.started_at).all()
    period = "N/A"
    if logs:
        period = f"{logs[0].started_at.date()} to {logs[-1].started_at.date()}"

    filepath = generate_pdf_report(
        user,
        result["feature_summary"],
        result,
        {"total_sessions": len(logs), "period": period},
    )

    report = Report(
        user_id=user_id,
        pdf_path=filepath,
        summary={"risk_profile": result["risk_profile"], "confidence": result["confidence"]},
    )
    db.session.add(report)
    db.session.commit()

    return jsonify({"report_id": report.id, "download_url": f"/api/v1/reports/{report.id}/download"}), 201


@reports_bp.route("/<report_id>/download", methods=["GET"])
@jwt_required()
def download_report(report_id):
    user_id = get_jwt_identity()
    report = Report.query.filter_by(id=report_id, user_id=user_id).first()
    if not report or not report.pdf_path:
        return jsonify({"error": "not_found", "message": "Report not found"}), 404

    return send_file(report.pdf_path, mimetype="application/pdf", as_attachment=True)


# ── Exercises ─────────────────────────────────────────────────────────────────

@exercises_bp.route("/recommended", methods=["GET"])
@jwt_required()
def recommended_exercises():
    user_id = get_jwt_identity()
    latest = (
        AIPrediction.query.filter_by(user_id=user_id)
        .order_by(AIPrediction.predicted_at.desc())
        .first()
    )
    risk = latest.risk_profile if latest else "baseline"
    exercises = get_recommended_exercises(risk)
    return jsonify({"exercises": exercises})
