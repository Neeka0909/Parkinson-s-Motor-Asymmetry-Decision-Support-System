import os
from pathlib import Path

from dotenv import load_dotenv

_root_env = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_root_env)
load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql://pdapp:pdapp_secret@127.0.0.1:15432/pdapp_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = 86400 * 7  # 7 days
    ML_MODEL_PATH = os.getenv("ML_MODEL_PATH", "../ml/models/risk_classifier.joblib")
