from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from app.config import Config
from app.models import db
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

    @app.route("/api/v1/health")
    def health():
        return jsonify({"status": "ok", "service": "motor-dss-backend"})

    return app
