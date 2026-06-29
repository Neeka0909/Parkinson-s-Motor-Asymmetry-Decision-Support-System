import os

import joblib
import numpy as np

from app.services.feature_engineering import build_feature_vector

FEATURE_ORDER = [
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

RECOMMENDATIONS = {
    "baseline": "Continue regular assessments. No sustained motor asymmetry detected.",
    "monitor": "Mild asymmetry trend detected. Continue daily assessments and track progress.",
    "elevated": "Sustained asymmetric motor patterns detected. Please consult your neurologist.",
    "referral": "Progressive motor degradation detected. Immediate neurologist consultation recommended.",
}


class MLInferenceEngine:
    def __init__(self, model_path=None):
        from flask import current_app

        self.model_path = model_path or current_app.config.get("ML_MODEL_PATH")
        self.model = None
        self._load_model()

    def _load_model(self):
        if self.model_path and os.path.exists(self.model_path):
            bundle = joblib.load(self.model_path)
            self.model = bundle["model"] if isinstance(bundle, dict) else bundle
        else:
            self.model = None

    def predict(self, user_id):
        features = build_feature_vector(user_id)
        vector = np.array([[features[k] for k in FEATURE_ORDER]])

        if self.model is not None:
            proba = self.model.predict_proba(vector)[0]
            idx = int(np.argmax(proba))
            risk_profile = RISK_LABELS[idx]
            confidence = float(proba[idx])
        else:
            risk_profile, confidence = self._rule_based_fallback(features)

        return {
            "risk_profile": risk_profile,
            "confidence": round(confidence, 3),
            "feature_summary": features,
            "recommendation": RECOMMENDATIONS[risk_profile],
        }

    def _rule_based_fallback(self, features):
        """Fallback when ML model file is not yet trained."""
        score = 0
        if abs(features["ft_asymmetry_trend"]) > 0.02:
            score += 1
        if features["sustained_asymmetry_flag"]:
            score += 2
        if features["performance_degradation_rate"] < -2:
            score += 1
        if features["rt_rolling_std_7d"] > 50:
            score += 1

        if score >= 4:
            return "referral", 0.75
        if score >= 3:
            return "elevated", 0.70
        if score >= 1:
            return "monitor", 0.65
        return "baseline", 0.80
