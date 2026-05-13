"""Inference for the Need_Maintenance classifier.

The trained Pipeline (preprocessor + classifier) lives in app/ml/model.pkl.
On startup, FastAPI's lifespan calls `load_model()` which fills the module-level
`_MODEL` dict; request handlers then call `predict_risk(car, db)`.

Six of the 13 features are derived from existing tables:
  - vehicle_age              from Car.year
  - service_history          COUNT(MaintenanceRecord)
  - last_service_days_ago    now - MAX(MaintenanceRecord.service_date)
  - reported_issues          COUNT(Alert)
  - maintenance_history      heuristic from service_history / vehicle_age
  - battery_status           heuristic from latest TelemetryLog.battery_voltage
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.models.car import Car
from app.models.device import Device
from app.models.maintenance_record import MaintenanceRecord
from app.models.telemetry_log import TelemetryLog

MODEL_PATH = Path(__file__).parent / "model.pkl"

_MODEL: dict[str, Any] | None = None


def load_model() -> None:
    """Load the pickled training payload into the module-level cache."""
    global _MODEL
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"ML model not found at {MODEL_PATH}. "
            "Run `python -m app.ml.train` first."
        )
    _MODEL = joblib.load(MODEL_PATH)


def get_model() -> dict[str, Any]:
    if _MODEL is None:
        raise RuntimeError("ML model not loaded. Did the FastAPI lifespan run?")
    return _MODEL


def _maintenance_history(service_count: int, vehicle_age: int) -> str:
    """Heuristic mapping to the dataset's Maintenance_History categories."""
    ratio = service_count / max(vehicle_age, 1)
    if ratio > 1:
        return "Good"
    if ratio >= 0.5:
        return "Average"
    return "Poor"


def _battery_status(voltage: float | None) -> str:
    """Heuristic mapping to the dataset's Battery_Status categories."""
    if voltage is None:
        return "Good"
    if voltage > 12.5:
        return "New"
    if voltage >= 12.0:
        return "Good"
    return "Weak"


async def build_feature_row(car: Car, db: AsyncSession) -> dict[str, Any]:
    """Collect 13-feature dict for a given Car. Issues 3 small SQL queries."""
    today = datetime.now(timezone.utc).date()
    vehicle_age = max(today.year - car.year, 0)

    service_stats = await db.execute(
        select(
            func.count(MaintenanceRecord.id),
            func.max(MaintenanceRecord.service_date),
        ).where(MaintenanceRecord.car_id == car.id)
    )
    service_count, last_service_date = service_stats.one()
    last_service_days_ago = (
        (today - last_service_date).days if last_service_date else 9999
    )

    reported_issues = await db.scalar(
        select(func.count(Alert.id)).where(Alert.car_id == car.id)
    )

    last_voltage = await db.scalar(
        select(TelemetryLog.battery_voltage)
        .join(Device, TelemetryLog.device_id == Device.id)
        .where(Device.car_id == car.id, TelemetryLog.battery_voltage.is_not(None))
        .order_by(TelemetryLog.timestamp.desc())
        .limit(1)
    )

    return {
        "body_type": car.body_type,
        "fuel_type": car.fuel_type,
        "transmission": car.transmission,
        "brake_condition": car.brake_condition,
        "owner_type": car.owner_type,
        "maintenance_history": _maintenance_history(service_count, vehicle_age),
        "battery_status": _battery_status(last_voltage),
        "engine_size": car.engine_size,
        "mileage": car.mileage,
        "vehicle_age": vehicle_age,
        "service_history": service_count,
        "last_service_days_ago": last_service_days_ago,
        "reported_issues": reported_issues or 0,
    }


async def predict_risk(car: Car, db: AsyncSession) -> float:
    """Return probability of Need_Maintenance == 1 in [0, 1]."""
    model = get_model()
    features = await build_feature_row(car, db)
    row = pd.DataFrame([features], columns=model["feature_columns"])
    proba = model["pipeline"].predict_proba(row)[0, 1]
    return float(proba)
