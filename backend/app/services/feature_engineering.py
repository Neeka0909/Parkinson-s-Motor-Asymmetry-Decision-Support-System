import os
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
from sqlalchemy import desc

from app.models import Biomarker, GameLog, db


def build_feature_vector(user_id):
    """Build longitudinal feature vector from user's game history."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=60)
    logs = (
        GameLog.query.filter(
            GameLog.user_id == user_id,
            GameLog.started_at >= cutoff,
        )
        .order_by(desc(GameLog.started_at))
        .all()
    )

    if not logs:
        return _empty_features()

    rows = []
    for log in logs:
        for bm in log.biomarkers:
            rows.append(
                {
                    "started_at": log.started_at,
                    "game_type": log.game_type,
                    "reaction_time_ms": bm.reaction_time_ms,
                    "flight_time_ms": bm.flight_time_ms,
                    "hold_time_ms": bm.hold_time_ms,
                    "hand_side": bm.hand_side,
                    "asymmetry_ratio": bm.asymmetry_ratio,
                    "accuracy_pct": bm.accuracy_pct,
                    "variance_ms": bm.variance_ms,
                }
            )

    if not rows:
        return _empty_features()

    df = pd.DataFrame(rows)
    now = datetime.now(timezone.utc)

    features = {}

    # 7-day rolling RT
    rt_7d = df[df["reaction_time_ms"].notna()]
    rt_recent = rt_7d[rt_7d["started_at"] >= now - timedelta(days=7)]
    features["rt_rolling_mean_7d"] = float(rt_recent["reaction_time_ms"].mean()) if len(rt_recent) else 400.0
    features["rt_rolling_std_7d"] = float(rt_recent["reaction_time_ms"].std()) if len(rt_recent) > 1 else 0.0

    # Flight time stats
    ft = df[df["flight_time_ms"].notna()]
    features["ft_mean"] = float(ft["flight_time_ms"].mean()) if len(ft) else 200.0
    features["ft_std"] = float(ft["flight_time_ms"].std()) if len(ft) > 1 else 0.0

    # Hold time stats
    ht = df[df["hold_time_ms"].notna()]
    features["ht_mean"] = float(ht["hold_time_ms"].mean()) if len(ht) else 150.0
    features["ht_std"] = float(ht["hold_time_ms"].std()) if len(ht) > 1 else 0.0

    # Asymmetry trends (30-day slope)
    asym = df[df["asymmetry_ratio"].notna()].sort_values("started_at")
    if len(asym) >= 3:
        x = np.arange(len(asym))
        features["ft_asymmetry_trend"] = float(np.polyfit(x, asym["asymmetry_ratio"].values, 1)[0])
    else:
        features["ft_asymmetry_trend"] = 0.0

    features["ht_asymmetry_trend"] = features["ft_asymmetry_trend"]

    # Session consistency
    session_scores = [log.score for log in logs if log.score]
    if len(session_scores) > 1:
        features["session_consistency"] = float(np.std(session_scores) / (np.mean(session_scores) + 1e-6))
    else:
        features["session_consistency"] = 0.0

    # Sustained asymmetry flag
    recent_asym = asym[asym["started_at"] >= now - timedelta(days=14)] if len(asym) else pd.DataFrame()
    threshold = 0.15  # 15% deviation from 1.0
    if len(recent_asym) >= 5:
        deviations = abs(recent_asym["asymmetry_ratio"] - 1.0)
        features["sustained_asymmetry_flag"] = int((deviations > threshold).sum() >= 5)
    else:
        features["sustained_asymmetry_flag"] = 0

    # Performance degradation (composite score slope)
    scores_df = pd.DataFrame(
        [{"started_at": log.started_at, "score": log.score} for log in logs if log.score]
    ).sort_values("started_at")
    if len(scores_df) >= 3:
        x = np.arange(len(scores_df))
        features["performance_degradation_rate"] = float(np.polyfit(x, scores_df["score"].values, 1)[0])
    else:
        features["performance_degradation_rate"] = 0.0

    features["total_sessions"] = len(logs)
    features["accuracy_mean"] = float(df["accuracy_pct"].mean()) if len(df) else 100.0

    return features


def _empty_features():
    return {
        "rt_rolling_mean_7d": 400.0,
        "rt_rolling_std_7d": 0.0,
        "ft_mean": 200.0,
        "ft_std": 0.0,
        "ht_mean": 150.0,
        "ht_std": 0.0,
        "ft_asymmetry_trend": 0.0,
        "ht_asymmetry_trend": 0.0,
        "session_consistency": 0.0,
        "sustained_asymmetry_flag": 0,
        "performance_degradation_rate": 0.0,
        "total_sessions": 0,
        "accuracy_mean": 100.0,
    }
