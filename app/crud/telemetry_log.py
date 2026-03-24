from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.telemetry_log import TelemetryLog
from app.models.device import Device
from app.schemas.telemetry_log import TelemetryLogCreate


def create_telemetry_log(
    db: Session,
    log: TelemetryLogCreate
) -> TelemetryLog:
    db_log = TelemetryLog(**log.model_dump())

    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    return db_log


def get_telemetry_logs_by_device(
    db: Session,
    device_id: int,
    skip: int = 0,
    limit: int = 100
) -> list[TelemetryLog]:
    return (
        db.query(TelemetryLog)
        .filter(TelemetryLog.device_id == device_id)
        .order_by(desc(TelemetryLog.timestamp))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_telemetry_logs_by_car(
    db: Session,
    car_id: int,
    skip: int = 0,
    limit: int = 100
) -> list[TelemetryLog]:
    return (
        db.query(TelemetryLog)
        .join(Device)
        .filter(Device.car_id == car_id)
        .order_by(desc(TelemetryLog.timestamp))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_latest_telemetry_by_car(
    db: Session,
    car_id: int
) -> TelemetryLog | None:
    return (
        db.query(TelemetryLog)
        .join(Device)
        .filter(Device.car_id == car_id)
        .order_by(desc(TelemetryLog.timestamp))
        .first()
    )