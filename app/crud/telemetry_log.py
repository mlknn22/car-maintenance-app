from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.car import Car
from app.models.device import Device
from app.models.telemetry_log import TelemetryLog


async def get_telemetry_logs_by_device(
    db: AsyncSession,
    device_id: int,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[TelemetryLog]:
    stmt = (
        select(TelemetryLog)
        .join(Device, TelemetryLog.device_id == Device.id)
        .join(Car, Device.car_id == Car.id)
        .where(TelemetryLog.device_id == device_id, Car.user_id == user_id)
        .order_by(desc(TelemetryLog.timestamp))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_telemetry_logs_by_car(
    db: AsyncSession,
    car_id: int,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[TelemetryLog]:
    stmt = (
        select(TelemetryLog)
        .join(Device, TelemetryLog.device_id == Device.id)
        .join(Car, Device.car_id == Car.id)
        .where(Device.car_id == car_id, Car.user_id == user_id)
        .order_by(desc(TelemetryLog.timestamp))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_latest_telemetry_by_car(
    db: AsyncSession,
    car_id: int,
    user_id: int,
) -> TelemetryLog | None:
    stmt = (
        select(TelemetryLog)
        .join(Device, TelemetryLog.device_id == Device.id)
        .join(Car, Device.car_id == Car.id)
        .where(Device.car_id == car_id, Car.user_id == user_id)
        .order_by(desc(TelemetryLog.timestamp))
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
