from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.models.car import Car
from app.schemas.alert import AlertCreate


async def _user_owns_car(db: AsyncSession, car_id: int, user_id: int) -> bool:
    stmt = select(Car.id).where(Car.id == car_id, Car.user_id == user_id)
    return (await db.execute(stmt)).scalar_one_or_none() is not None


async def create_alert(
    db: AsyncSession,
    alert: AlertCreate,
    user_id: int,
) -> Alert | None:
    if not await _user_owns_car(db, alert.car_id, user_id):
        return None

    db_alert = Alert(**alert.model_dump())
    db.add(db_alert)
    await db.commit()
    await db.refresh(db_alert)
    return db_alert


async def get_alerts_by_car(
    db: AsyncSession,
    car_id: int,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False,
) -> list[Alert]:
    stmt = (
        select(Alert)
        .join(Car, Alert.car_id == Car.id)
        .where(Alert.car_id == car_id, Car.user_id == user_id)
        .order_by(desc(Alert.timestamp))
    )
    if unread_only:
        stmt = stmt.where(Alert.is_read == False)
    stmt = stmt.offset(skip).limit(limit)

    result = await db.execute(stmt)
    return result.scalars().all()


async def get_alert_by_id(
    db: AsyncSession,
    alert_id: int,
    user_id: int,
) -> Alert | None:
    stmt = (
        select(Alert)
        .join(Car, Alert.car_id == Car.id)
        .where(Alert.id == alert_id, Car.user_id == user_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def mark_as_read(
    db: AsyncSession,
    alert_id: int,
    user_id: int,
) -> Alert | None:
    db_alert = await get_alert_by_id(db, alert_id, user_id)
    if not db_alert:
        return None

    db_alert.is_read = True
    await db.commit()
    await db.refresh(db_alert)
    return db_alert


async def mark_all_as_read(
    db: AsyncSession,
    car_id: int,
    user_id: int,
) -> int:
    owned_car_ids = select(Car.id).where(Car.id == car_id, Car.user_id == user_id)
    stmt = (
        update(Alert)
        .where(Alert.car_id.in_(owned_car_ids), Alert.is_read == False)
        .values(is_read=True)
        .execution_options(synchronize_session=False)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount


async def delete_alert(
    db: AsyncSession,
    alert_id: int,
    user_id: int,
) -> Alert | None:
    db_alert = await get_alert_by_id(db, alert_id, user_id)
    if not db_alert:
        return None

    await db.delete(db_alert)
    await db.commit()
    return db_alert
