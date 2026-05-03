from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.telemetry_log import TelemetryLog
from app.models.device import Device
from app.schemas.telemetry_log import TelemetryLogCreate


async def create_telemetry_log(
    db: AsyncSession,
    log: TelemetryLogCreate,
) -> TelemetryLog:
    db_log = TelemetryLog(**log.model_dump())
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log


async def get_telemetry_logs_by_device(
    db: AsyncSession,
    device_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[TelemetryLog]:
    stmt = (
        select(TelemetryLog)
        .where(TelemetryLog.device_id == device_id)
        .order_by(desc(TelemetryLog.timestamp))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_telemetry_logs_by_car(
    db: AsyncSession,
    car_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[TelemetryLog]:
    stmt = (
        select(TelemetryLog)
        .join(Device)
        .where(Device.car_id == car_id)
        .order_by(desc(TelemetryLog.timestamp))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_latest_telemetry_by_car(
    db: AsyncSession,
    car_id: int,
) -> TelemetryLog | None:
    stmt = (
        select(TelemetryLog)
        .join(Device)
        .where(Device.car_id == car_id)
        .order_by(desc(TelemetryLog.timestamp))
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
