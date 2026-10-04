"""
Train, evaluate, cross-validate, and compare SVM, Random Forest, XGBoost, and KNN
on the motor biomarker research dataset.

Run:
    python ml/train_model.py
    python train_model.py
"""

from __future__ import annotations

import argparse
import os
import warnings
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from xgboost import XGBClassifier

warnings.filterwarnings("ignore", category=UserWarning)

RANDOM_STATE = 42
PROJECT_TITLE = "Motor Biomarker Risk"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
DEFAULT_DATASET = os.path.join(REPO_ROOT, "Traning Data", "motor_biomarker_dataset.csv")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs")
MODELS_DIR = os.path.join(SCRIPT_DIR, "models")

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

TARGET_COLUMN = "risk_profile"
PREFERRED_LABEL_ORDER = ["baseline", "monitor", "elevated", "referral"]
MODEL_GRID_ORDER = ["SVM", "Random Forest", "XGBoost", "KNN"]


@dataclass
class ModelResult:
    name: str
    estimator: Any
    training_accuracy: float
    validation_accuracy: float
    test_accuracy: float
    balanced_accuracy: float
    macro_precision: float
    macro_recall: float
    macro_f1: float
    generalisation_gap: float
    cv_scores: np.ndarray
    y_test_pred: np.ndarray

    @property
    def cv_mean(self) -> float:
        return float(np.mean(self.cv_scores))

    @property
    def cv_std(self) -> float:
        return float(np.std(self.cv_scores))


def resolve_class_names(y: pd.Series) -> list[str]:
    """Extract labels dynamically, preserving preferred order when present."""
    present = {str(v) for v in y.dropna().unique()}
    ordered = [label for label in PREFERRED_LABEL_ORDER if label in present]
    remaining = sorted(present - set(ordered))
    return ordered + remaining


def encode_labels(y: pd.Series, class_names: list[str]) -> np.ndarray:
    mapping = {name: idx for idx, name in enumerate(class_names)}
    unknown = sorted(set(y.astype(str)) - set(mapping))
    if unknown:
        raise ValueError(f"Unexpected target labels: {unknown}")
    return y.astype(str).map(mapping).to_numpy(dtype=int)


def load_and_clean_dataset(dataset_path: str) -> tuple[pd.DataFrame, list[str]]:
    print("=" * 72)
    print("1. DATA PREPROCESSING & SPLITTING")
    print("=" * 72)

    df = pd.read_csv(dataset_path)
    print(f"\nDataset path          : {dataset_path}")
    print(f"Initial shape         : {df.shape}")

    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Target column '{TARGET_COLUMN}' not found in dataset.")

    missing_features = [c for c in FEATURE_COLUMNS if c not in df.columns]
    if missing_features:
        raise ValueError(f"Missing feature columns: {missing_features}")

    print("\nTarget distribution (before cleaning):")
    print(df[TARGET_COLUMN].value_counts(dropna=False).to_string())

    required_cols = FEATURE_COLUMNS + [TARGET_COLUMN]
    before = len(df)
    df = df.dropna(subset=required_cols).copy()
    df[TARGET_COLUMN] = df[TARGET_COLUMN].astype(str).str.strip()
    df = df[df[TARGET_COLUMN] != ""].reset_index(drop=True)
    after = len(df)

    print(f"\nRows removed (missing/invalid): {before - after}")
    print(f"Shape after cleaning  : {df.shape}")

    class_names = resolve_class_names(df[TARGET_COLUMN])
    print(f"\nClass labels (dynamic): {class_names}")
    print("Target mapping:")
    for idx, name in enumerate(class_names):
        print(f"  {idx} = {name}")

    print("\nTarget distribution (after cleaning):")
    print(df[TARGET_COLUMN].value_counts().reindex(class_names).to_string())
    return df, class_names


def split_dataset(
    df: pd.DataFrame, class_names: list[str]
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    X = df[FEATURE_COLUMNS].astype(float)
    y = encode_labels(df[TARGET_COLUMN], class_names)

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, random_state=RANDOM_STATE, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=RANDOM_STATE, stratify=y_temp
    )

    print("\nSplit shapes (70% / 15% / 15%, stratified):")
    print(f"  Training   : X={X_train.shape}, y={y_train.shape}")
    print(f"  Validation : X={X_val.shape}, y={y_val.shape}")
    print(f"  Test       : X={X_test.shape}, y={y_test.shape}")
    return X_train, X_val, X_test, y_train, y_val, y_test


def scale_features(
    X_train: pd.DataFrame, X_val: pd.DataFrame, X_test: pd.DataFrame
) -> tuple[np.ndarray, np.ndarray, np.ndarray, StandardScaler]:
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    print("\nStandardScaler fitted on training data only; applied to val/test.")
    return X_train_scaled, X_val_scaled, X_test_scaled, scaler


def build_estimators(n_classes: int) -> dict[str, Any]:
    return {
        "SVM": CalibratedClassifierCV(
            estimator=SVC(
                kernel="rbf",
                C=1.0,
                gamma="scale",
                class_weight="balanced",
                random_state=RANDOM_STATE,
            ),
            method="sigmoid",
            cv=3,
            ensemble=False,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_leaf=5,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "XGBoost": XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="multi:softprob",
            num_class=n_classes,
            eval_metric="mlogloss",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "KNN": KNeighborsClassifier(
            n_neighbors=7,
            weights="distance",
            metric="minkowski",
            p=2,
            n_jobs=-1,
        ),
    }


def stratified_cv_scores(estimator: Any, X_train: pd.DataFrame, y_train: np.ndarray) -> np.ndarray:
    """5-fold CV with scaler refit inside each fold (no leakage)."""
    pipe = Pipeline([("scaler", StandardScaler()), ("clf", deepcopy(estimator))])
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    return cross_val_score(pipe, X_train, y_train, cv=cv, scoring="accuracy", n_jobs=-1)


def evaluate_estimator(
    name: str,
    estimator: Any,
    X_train_scaled: np.ndarray,
    X_val_scaled: np.ndarray,
    X_test_scaled: np.ndarray,
    X_train_raw: pd.DataFrame,
    y_train: np.ndarray,
    y_val: np.ndarray,
    y_test: np.ndarray,
    class_names: list[str],
) -> ModelResult:
    print("\n" + "-" * 72)
    print(f"MODEL: {name}")
    print("-" * 72)

    print("5-Fold Stratified Cross Validation (on training set):")
    cv_scores = stratified_cv_scores(estimator, X_train_raw, y_train)
    print(f"  Fold Scores : {np.array2string(cv_scores, precision=4, separator=', ')}")
    print(f"  Mean        : {cv_scores.mean():.4f}")
    print(f"  Std         : {cv_scores.std():.4f}")

    estimator.fit(X_train_scaled, y_train)

    y_train_pred = estimator.predict(X_train_scaled)
    y_val_pred = estimator.predict(X_val_scaled)
    y_test_pred = estimator.predict(X_test_scaled)

    training_accuracy = accuracy_score(y_train, y_train_pred)
    validation_accuracy = accuracy_score(y_val, y_val_pred)
    test_accuracy = accuracy_score(y_test, y_test_pred)
    bal_acc = balanced_accuracy_score(y_test, y_test_pred)
    macro_precision = precision_score(y_test, y_test_pred, average="macro", zero_division=0)
    macro_recall = recall_score(y_test, y_test_pred, average="macro", zero_division=0)
    macro_f1 = f1_score(y_test, y_test_pred, average="macro", zero_division=0)
    generalisation_gap = training_accuracy - test_accuracy

    print(f"\nTraining Accuracy     : {training_accuracy:.4f}")
    print(f"Validation Accuracy   : {validation_accuracy:.4f}")
    print(f"Test Accuracy         : {test_accuracy:.4f}")
    print(f"Balanced Accuracy     : {bal_acc:.4f}")
    print(f"Macro Precision       : {macro_precision:.4f}")
    print(f"Macro Recall          : {macro_recall:.4f}")
    print(f"Macro F1              : {macro_f1:.4f}")
    print(f"Generalisation Gap    : {generalisation_gap:.4f}  (Train - Test)")
    print("\nTest Classification Report:")
    print(
        classification_report(
            y_test,
            y_test_pred,
            labels=list(range(len(class_names))),
            target_names=class_names,
            digits=4,
            zero_division=0,
        )
    )

    return ModelResult(
        name=name,
        estimator=estimator,
        training_accuracy=training_accuracy,
        validation_accuracy=validation_accuracy,
        test_accuracy=test_accuracy,
        balanced_accuracy=bal_acc,
        macro_precision=macro_precision,
        macro_recall=macro_recall,
        macro_f1=macro_f1,
        generalisation_gap=generalisation_gap,
        cv_scores=cv_scores,
        y_test_pred=y_test_pred,
    )


def print_comparison_table(results: list[ModelResult]) -> None:
    print("\n" + "=" * 72)
    print("FINAL MODEL COMPARISON")
    print("=" * 72)

    headers = [
        "Model",
        "Training Accuracy",
        "Validation Accuracy",
        "Test Accuracy",
        "Balanced Accuracy",
        "Macro Precision",
        "Macro Recall",
        "Macro F1",
        "Generalisation Gap",
        "5-Fold CV Mean",
        "5-Fold CV Std",
    ]
    rows = [
        [
            r.name,
            f"{r.training_accuracy:.4f}",
            f"{r.validation_accuracy:.4f}",
            f"{r.test_accuracy:.4f}",
            f"{r.balanced_accuracy:.4f}",
            f"{r.macro_precision:.4f}",
            f"{r.macro_recall:.4f}",
            f"{r.macro_f1:.4f}",
            f"{r.generalisation_gap:.4f}",
            f"{r.cv_mean:.4f}",
            f"{r.cv_std:.4f}",
        ]
        for r in results
    ]

    widths = [max(len(h), max(len(row[i]) for row in rows)) for i, h in enumerate(headers)]
    print(" | ".join(h.ljust(widths[i]) for i, h in enumerate(headers)))
    print("-+-".join("-" * widths[i] for i in range(len(headers))))
    for row in rows:
        print(" | ".join(row[i].ljust(widths[i]) for i in range(len(headers))))


def select_best_model(results: list[ModelResult]) -> ModelResult:
    best = sorted(
        results,
        key=lambda r: (r.cv_mean, r.test_accuracy, r.macro_f1),
        reverse=True,
    )[0]

    print("\n" + "=" * 72)
    print("BEST MODEL")
    print("=" * 72)
    print(f"Selected Best Model   : {best.name}")
    print(f"Best CV Accuracy      : {best.cv_mean:.4f}")
    print(f"Best Test Accuracy    : {best.test_accuracy:.4f}")
    print(f"Best Macro F1         : {best.macro_f1:.4f}")
    return best


def plot_confusion_matrices(
    results: list[ModelResult],
    y_test: np.ndarray,
    class_names: list[str],
    output_path: str,
) -> str:
    by_name = {r.name: r for r in results}
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(
        f"{PROJECT_TITLE} - Confusion Matrices of All ML Models",
        fontsize=14,
        fontweight="bold",
    )

    labels = list(range(len(class_names)))
    for name, ax in zip(MODEL_GRID_ORDER, axes.ravel()):
        result = by_name[name]
        cm = confusion_matrix(y_test, result.y_test_pred, labels=labels)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
        disp.plot(ax=ax, cmap="Blues", colorbar=False, values_format="d")
        ax.set_title(name)
        ax.set_xlabel("Predicted Class")
        ax.set_ylabel("Actual Class")
        ax.set_xticks(labels)
        ax.set_yticks(labels)
        ax.set_xticklabels(class_names, rotation=45, ha="right")
        ax.set_yticklabels(class_names)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"\nConfusion matrix figure saved to: {output_path}")
    return output_path


def save_best_bundle(
    best: ModelResult,
    scaler: StandardScaler,
    class_names: list[str],
) -> str:
    """
    Save a Pipeline(scaler, clf) as `model` so existing inference can call
    predict_proba on raw feature vectors without a separate scaling step.
    """
    os.makedirs(MODELS_DIR, exist_ok=True)
    model_path = os.path.join(MODELS_DIR, "risk_classifier.joblib")

    pipeline = Pipeline([("scaler", scaler), ("clf", best.estimator)])
    joblib.dump(
        {
            "model": pipeline,
            "scaler": scaler,
            "features": FEATURE_COLUMNS,
            "class_names": class_names,
            "model_name": best.name,
            "metrics": {
                "cv_mean": best.cv_mean,
                "test_accuracy": best.test_accuracy,
                "macro_f1": best.macro_f1,
            },
        },
        model_path,
    )
    print(f"Best model bundle saved to: {model_path}")
    return model_path


def train_and_compare(dataset_path: str = DEFAULT_DATASET) -> dict[str, Any]:
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    df, class_names = load_and_clean_dataset(dataset_path)
    X_train, X_val, X_test, y_train, y_val, y_test = split_dataset(df, class_names)
    X_train_scaled, X_val_scaled, X_test_scaled, scaler = scale_features(
        X_train, X_val, X_test
    )

    print("\n" + "=" * 72)
    print("2. PER-MODEL TRAINING & EVALUATION")
    print("=" * 72)

    estimators = build_estimators(n_classes=len(class_names))
    results = [
        evaluate_estimator(
            name=name,
            estimator=estimator,
            X_train_scaled=X_train_scaled,
            X_val_scaled=X_val_scaled,
            X_test_scaled=X_test_scaled,
            X_train_raw=X_train,
            y_train=y_train,
            y_val=y_val,
            y_test=y_test,
            class_names=class_names,
        )
        for name, estimator in estimators.items()
    ]

    print_comparison_table(results)
    best = select_best_model(results)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    cm_path = os.path.join(OUTPUT_DIR, "confusion_matrices.png")
    plot_confusion_matrices(results, y_test, class_names, cm_path)
    model_path = save_best_bundle(best, scaler, class_names)

    return {
        "results": results,
        "best": best,
        "confusion_matrix_path": cm_path,
        "model_path": model_path,
        "class_names": class_names,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train and compare motor biomarker risk classification models."
    )
    parser.add_argument(
        "--dataset",
        default=DEFAULT_DATASET,
        help="Path to motor_biomarker_dataset.csv",
    )
    args = parser.parse_args()
    train_and_compare(dataset_path=args.dataset)
