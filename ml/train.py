"""
Train risk classifier on synthetic proxy dataset.
Run: python train.py
"""

import os

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

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


def generate_synthetic_data(n_samples=2000, seed=42):
    """Generate synthetic longitudinal motor profiles for model validation."""
    rng = np.random.default_rng(seed)
    rows = []

    for _ in range(n_samples):
        profile = rng.choice(RISK_LABELS, p=[0.50, 0.25, 0.15, 0.10])

        if profile == "baseline":
            rt_mean = rng.normal(380, 30)
            rt_std = rng.normal(20, 8)
            asym_trend = rng.normal(0, 0.005)
            sustained = 0
            degradation = rng.normal(0.5, 1)
        elif profile == "monitor":
            rt_mean = rng.normal(400, 35)
            rt_std = rng.normal(30, 10)
            asym_trend = rng.normal(0.02, 0.01)
            sustained = rng.choice([0, 1], p=[0.7, 0.3])
            degradation = rng.normal(-0.5, 1.5)
        elif profile == "elevated":
            rt_mean = rng.normal(430, 40)
            rt_std = rng.normal(45, 12)
            asym_trend = rng.normal(0.04, 0.015)
            sustained = rng.choice([0, 1], p=[0.3, 0.7])
            degradation = rng.normal(-2, 2)
        else:  # referral
            rt_mean = rng.normal(470, 50)
            rt_std = rng.normal(60, 15)
            asym_trend = rng.normal(0.06, 0.02)
            sustained = 1
            degradation = rng.normal(-5, 2)

        rows.append(
            {
                "rt_rolling_mean_7d": max(rt_mean, 200),
                "rt_rolling_std_7d": max(rt_std, 0),
                "ft_mean": max(rng.normal(210, 40), 80),
                "ft_std": max(rng.normal(25, 10), 0),
                "ht_mean": max(rng.normal(155, 30), 60),
                "ht_std": max(rng.normal(20, 8), 0),
                "ft_asymmetry_trend": asym_trend,
                "ht_asymmetry_trend": asym_trend + rng.normal(0, 0.005),
                "session_consistency": max(rng.normal(0.15, 0.08), 0),
                "sustained_asymmetry_flag": sustained,
                "performance_degradation_rate": degradation,
                "total_sessions": int(rng.integers(5, 60)),
                "accuracy_mean": max(min(rng.normal(92, 5), 100), 60),
                "risk_profile": profile,
            }
        )

    return pd.DataFrame(rows)


def train_model():
    print("Generating synthetic dataset...")
    df = generate_synthetic_data()

    X = df[FEATURE_COLUMNS]
    y = df["risk_profile"]

    le = LabelEncoder()
    le.fit(RISK_LABELS)
    y_encoded = le.transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_leaf=5,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=RISK_LABELS))

    models_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, "risk_classifier.joblib")

    joblib.dump({"model": model, "label_encoder": le, "features": FEATURE_COLUMNS}, model_path)
    print(f"\nModel saved to {model_path}")
    return model_path


if __name__ == "__main__":
    train_model()
