import os
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
_root_env = REPO_ROOT / ".env"
load_dotenv(_root_env)
load_dotenv()


def _resolve_ml_model_path() -> str:
    raw = os.getenv("ML_MODEL_PATH", "ml/models/risk_classifier.joblib")
    path = Path(raw)
    if not path.is_absolute():
        # Prefer repo-root relative paths so cwd does not matter.
        candidates = [
            REPO_ROOT / raw,
            REPO_ROOT / "ml" / "models" / "risk_classifier.joblib",
            Path.cwd() / raw,
        ]
        for candidate in candidates:
            if candidate.exists():
                return str(candidate.resolve())
        return str((REPO_ROOT / "ml" / "models" / "risk_classifier.joblib").resolve())
    return str(path)


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me-32chars-min")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-change-me-32chars")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql://pdapp:pdapp_secret@127.0.0.1:15432/pdapp_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = 86400 * 7  # 7 days
    ML_MODEL_PATH = _resolve_ml_model_path()
