"""Standalone inference script for testing."""

import json
import sys

import joblib
import numpy as np

FEATURE_COLUMNS = [
    "rt_rolling_mean_7d",
    "rt_rolling_std_7d",
    "ft_mean",
    "ft_std",
    "ht_mean",
    "ht_std",
    "ft_asymmetry_trend",
    "ht_asymmetry_trend",
    "session_consistency",
    "sustained_asymmetry_flag",
    "performance_degradation_rate",
    "total_sessions",
    "accuracy_mean",
]

RISK_LABELS = ["baseline", "monitor", "elevated", "referral"]


def predict(model_path, features_dict):
    bundle = joblib.load(model_path)
    model = bundle["model"]
    vector = np.array([[features_dict[k] for k in FEATURE_COLUMNS]])
    proba = model.predict_proba(vector)[0]
    idx = int(np.argmax(proba))
    return {"risk_profile": RISK_LABELS[idx], "confidence": float(proba[idx])}


if __name__ == "__main__":
    sample = {
        "rt_rolling_mean_7d": 420,
        "rt_rolling_std_7d": 45,
        "ft_mean": 230,
        "ft_std": 35,
        "ht_mean": 170,
        "ht_std": 28,
        "ft_asymmetry_trend": 0.035,
        "ht_asymmetry_trend": 0.03,
        "session_consistency": 0.22,
        "sustained_asymmetry_flag": 1,
        "performance_degradation_rate": -3.5,
        "total_sessions": 25,
        "accuracy_mean": 88,
    }
    path = sys.argv[1] if len(sys.argv) > 1 else "models/risk_classifier.joblib"
    result = predict(path, sample)
    print(json.dumps(result, indent=2))
