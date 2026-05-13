"""Train Need_Maintenance classifier on the Kaggle Vehicle Maintenance Dataset.

Run: python -m app.ml.train

Compares 3 candidates (LogisticRegression / RandomForest / HistGradientBoosting)
on F1 + ROC-AUC over a stratified 80/20 split, dumps the winning Pipeline
(preprocessor + classifier) to app/ml/model.pkl together with the feature
column order so app/ml/predict.py can rebuild the input DataFrame at inference.
"""
from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

CSV_PATH = Path(__file__).resolve().parents[2] / "vehicle_maintenance_data.csv"
MODEL_PATH = Path(__file__).parent / "model.pkl"

NOMINAL = ["body_type", "fuel_type", "transmission"]
ORDINAL = ["brake_condition", "owner_type", "maintenance_history", "battery_status"]
# Ordered worst -> best so OrdinalEncoder gives higher integers to better states.
ORDINAL_CATEGORIES = [
    ["Worn Out", "Good", "New"],
    ["Third", "Second", "First"],
    ["Poor", "Average", "Good"],
    ["Weak", "Good", "New"],
]
NUMERIC = [
    "engine_size",
    "mileage",
    "vehicle_age",
    "service_history",
    "last_service_days_ago",
    "reported_issues",
]
TRAINING_FEATURES = NOMINAL + ORDINAL + NUMERIC
TARGET = "Need_Maintenance"


def load_dataset(csv_path: Path) -> pd.DataFrame:
    """Map raw Kaggle columns to the 13-feature schema used at inference."""
    df = pd.read_csv(csv_path)

    last_service = pd.to_datetime(df["Last_Service_Date"])
    # Anchor relative-days-ago to the newest service date in the dataset.
    # At inference we use (now - last_service).days; the encoding is identical,
    # only the anchor differs (a known and accepted domain shift).
    reference = last_service.max()
    last_service_days_ago = (reference - last_service).dt.days

    return pd.DataFrame({
        "body_type": df["Vehicle_Model"],
        "fuel_type": df["Fuel_Type"],
        "transmission": df["Transmission_Type"],
        "brake_condition": df["Brake_Condition"],
        "owner_type": df["Owner_Type"],
        "maintenance_history": df["Maintenance_History"],
        "battery_status": df["Battery_Status"],
        "engine_size": df["Engine_Size"],
        # Dataset's "Mileage" is a noisy duplicate of Odometer_Reading -- use Odometer.
        "mileage": df["Odometer_Reading"],
        "vehicle_age": df["Vehicle_Age"],
        "service_history": df["Service_History"],
        "last_service_days_ago": last_service_days_ago,
        "reported_issues": df["Reported_Issues"],
        TARGET: df[TARGET].astype(int),
    })


def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("nom", OneHotEncoder(handle_unknown="ignore", sparse_output=False), NOMINAL),
            (
                "ord",
                OrdinalEncoder(
                    categories=ORDINAL_CATEGORIES,
                    handle_unknown="use_encoded_value",
                    unknown_value=-1,
                ),
                ORDINAL,
            ),
            ("num", StandardScaler(), NUMERIC),
        ]
    )


def candidates() -> dict[str, object]:
    return {
        "logreg": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "random_forest": RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            n_jobs=-1,
            class_weight="balanced",
        ),
        "hgb": HistGradientBoostingClassifier(random_state=42),
    }


def main() -> None:
    print(f"loading {CSV_PATH}")
    df = load_dataset(CSV_PATH)

    X = df[TRAINING_FEATURES]
    y = df[TARGET]
    print(f"rows={len(df)} positive_rate={y.mean():.3f}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42,
    )

    results: dict[str, dict[str, float]] = {}
    pipelines: dict[str, Pipeline] = {}

    for name, clf in candidates().items():
        pipe = Pipeline([("prep", build_preprocessor()), ("clf", clf)])
        pipe.fit(X_train, y_train)
        pred = pipe.predict(X_test)
        proba = pipe.predict_proba(X_test)[:, 1]
        results[name] = {
            "f1": f1_score(y_test, pred),
            "roc_auc": roc_auc_score(y_test, proba),
        }
        pipelines[name] = pipe
        print(f"{name:>14}  f1={results[name]['f1']:.4f}  roc_auc={results[name]['roc_auc']:.4f}")

    winner = max(results, key=lambda n: results[n]["roc_auc"])
    print(f"\nwinner: {winner}  metrics={results[winner]}")

    payload = {
        "pipeline": pipelines[winner],
        "feature_columns": TRAINING_FEATURES,
        "model_name": winner,
        "metrics": results[winner],
    }
    joblib.dump(payload, MODEL_PATH)
    print(f"saved -> {MODEL_PATH}")


if __name__ == "__main__":
    main()
