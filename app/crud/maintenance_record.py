from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.car import Car
from app.models.maintenance_record import MaintenanceRecord
from app.schemas.maintenance_record import MaintenanceRecordCreate, MaintenanceRecordUpdate


async def _user_owns_car(db: AsyncSession, car_id: int, user_id: int) -> bool:
    stmt = select(Car.id).where(Car.id == car_id, Car.user_id == user_id)
    return (await db.execute(stmt)).scalar_one_or_none() is not None


async def create_maintenance_record(
    db: AsyncSession,
    record: MaintenanceRecordCreate,
    user_id: int,
) -> MaintenanceRecord | None:
    if not await _user_owns_car(db, record.car_id, user_id):
        return None

    db_record = MaintenanceRecord(**record.model_dump())
    db.add(db_record)
    await db.commit()
    await db.refresh(db_record)
    return db_record


async def get_maintenance_records_by_car(
    db: AsyncSession,
    car_id: int,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[MaintenanceRecord]:
    stmt = (
        select(MaintenanceRecord)
        .join(Car, MaintenanceRecord.car_id == Car.id)
        .where(MaintenanceRecord.car_id == car_id, Car.user_id == user_id)
        .order_by(MaintenanceRecord.service_date.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_maintenance_record_by_id(
    db: AsyncSession,
    record_id: int,
    user_id: int,
) -> MaintenanceRecord | None:
    stmt = (
        select(MaintenanceRecord)
        .join(Car, MaintenanceRecord.car_id == Car.id)
        .where(MaintenanceRecord.id == record_id, Car.user_id == user_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_maintenance_record(
    db: AsyncSession,
    record_id: int,
    record_data: MaintenanceRecordUpdate,
    user_id: int,
) -> MaintenanceRecord | None:
    db_record = await get_maintenance_record_by_id(db, record_id, user_id)
    if not db_record:
        return None

    update_data = record_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_record, field, value)

    await db.commit()
    await db.refresh(db_record)
    return db_record


async def delete_maintenance_record(
    db: AsyncSession,
    record_id: int,
    user_id: int,
) -> MaintenanceRecord | None:
    db_record = await get_maintenance_record_by_id(db, record_id, user_id)
    if not db_record:
        return None

    await db.delete(db_record)
    await db.commit()
    return db_record
