import uuid
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


def utcnow():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    handedness = db.Column(db.String(20), nullable=False, default="right")
    language_pref = db.Column(db.String(10), nullable=False, default="en")
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    game_logs = db.relationship("GameLog", backref="user", lazy="dynamic")
    predictions = db.relationship("AIPrediction", backref="user", lazy="dynamic")
    exercise_plans = db.relationship("ExercisePlan", backref="user", lazy="dynamic")
    reports = db.relationship("Report", backref="user", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "age": self.age,
            "handedness": self.handedness,
            "language_pref": self.language_pref,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class GameLog(db.Model):
    __tablename__ = "game_logs"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    game_type = db.Column(db.String(30), nullable=False)
    device_orientation = db.Column(db.String(20), default="portrait")
    time_of_day = db.Column(db.String(20), default="morning")
    score = db.Column(db.Integer, default=0)
    duration_ms = db.Column(db.Integer, default=0)
    raw_events = db.Column(db.JSON, default=list)
    started_at = db.Column(db.DateTime, nullable=False)
    completed_at = db.Column(db.DateTime)

    biomarkers = db.relationship("Biomarker", backref="game_log", lazy="dynamic")

    def to_dict(self, include_biomarkers=False):
        data = {
            "id": self.id,
            "game_type": self.game_type,
            "device_orientation": self.device_orientation,
            "time_of_day": self.time_of_day,
            "score": self.score,
            "duration_ms": self.duration_ms,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
        if include_biomarkers:
            data["biomarkers"] = [b.to_dict() for b in self.biomarkers]
        return data


class Biomarker(db.Model):
    __tablename__ = "biomarkers"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    game_log_id = db.Column(
        db.String(36), db.ForeignKey("game_logs.id"), nullable=False, index=True
    )
    reaction_time_ms = db.Column(db.Float)
    flight_time_ms = db.Column(db.Float)
    hold_time_ms = db.Column(db.Float)
    hand_side = db.Column(db.String(20))
    asymmetry_ratio = db.Column(db.Float)
    accuracy_pct = db.Column(db.Float)
    variance_ms = db.Column(db.Float)

    def to_dict(self):
        return {
            "id": self.id,
            "reaction_time_ms": self.reaction_time_ms,
            "flight_time_ms": self.flight_time_ms,
            "hold_time_ms": self.hold_time_ms,
            "hand_side": self.hand_side,
            "asymmetry_ratio": self.asymmetry_ratio,
            "accuracy_pct": self.accuracy_pct,
            "variance_ms": self.variance_ms,
        }


class AIPrediction(db.Model):
    __tablename__ = "ai_predictions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    risk_profile = db.Column(db.String(20), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    feature_vector = db.Column(db.JSON, default=dict)
    model_version = db.Column(db.String(50), default="1.0.0")
    predicted_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "risk_profile": self.risk_profile,
            "confidence": self.confidence,
            "feature_vector": self.feature_vector,
            "model_version": self.model_version,
            "predicted_at": self.predicted_at.isoformat() if self.predicted_at else None,
        }


class ExercisePlan(db.Model):
    __tablename__ = "exercise_plans"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    exercise_key = db.Column(db.String(100), nullable=False)
    title_en = db.Column(db.String(255))
    title_si = db.Column(db.String(255))
    instructions_en = db.Column(db.Text)
    instructions_si = db.Column(db.Text)
    assigned_at = db.Column(db.DateTime, default=utcnow)
    completed_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "exercise_key": self.exercise_key,
            "title_en": self.title_en,
            "title_si": self.title_si,
            "instructions_en": self.instructions_en,
            "instructions_si": self.instructions_si,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    pdf_path = db.Column(db.String(500))
    summary = db.Column(db.JSON, default=dict)
    generated_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "pdf_path": self.pdf_path,
            "summary": self.summary,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
        }
