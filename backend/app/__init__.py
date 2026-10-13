import os
import traceback

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from sqlalchemy import inspect, text
from werkzeug.exceptions import HTTPException

from app.config import Config
from app.models import User, db
from app.routes import (
    auth_bp,
    exercises_bp,
    games_bp,
    predictions_bp,
    reports_bp,
)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    Migrate(app, db)
    JWTManager(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(games_bp, url_prefix="/api/v1/games")
    app.register_blueprint(predictions_bp, url_prefix="/api/v1/predictions")
    app.register_blueprint(reports_bp, url_prefix="/api/v1/reports")
    app.register_blueprint(exercises_bp, url_prefix="/api/v1/exercises")

    @app.errorhandler(Exception)
    def handle_unexpected_error(err):
        if isinstance(err, HTTPException):
            return (
                jsonify(
                    {
                        "error": err.name.lower().replace(" ", "_"),
                        "message": err.description,
                    }
                ),
                err.code,
            )
        app.logger.error("Unhandled error: %s\n%s", err, traceback.format_exc())
        return (
            jsonify(
                {
                    "error": "internal_error",
                    "message": str(err) or "Internal server error",
                }
            ),
            500,
        )

    @app.route("/api/v1/health")
    def health():
        db_ok = False
        tables_ok = False
        user_count = None
        db_error = None
        try:
            db.session.execute(text("SELECT 1"))
            db_ok = True
            tables = set(inspect(db.engine).get_table_names())
            tables_ok = "users" in tables
            if tables_ok:
                user_count = User.query.count()
        except Exception as exc:
            db_error = str(exc)

        model_path = app.config.get("ML_MODEL_PATH")
        return jsonify(
            {
                "status": "ok" if db_ok and tables_ok else "degraded",
                "service": "motor-dss-backend",
                "database": {
                    "connected": db_ok,
                    "tables_ready": tables_ok,
                    "user_count": user_count,
                    "error": db_error,
                },
                "ml_model": {
                    "path": model_path,
                    "exists": bool(model_path and os.path.exists(model_path)),
                },
                "hint": None
                if db_ok and tables_ok
                else "Run: docker compose up -d db && cd backend && python init_db.py",
            }
        )

    return app
