from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertUpdate


async def create_alert(db: AsyncSession, alert: AlertCreate) -> Alert:
    db_alert = Alert(**alert.model_dump())
    db.add(db_alert)
    await db.commit()
    await db.refresh(db_alert)
    return db_alert


async def get_alerts_by_car(
    db: AsyncSession,
    car_id: int,
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False,
) -> list[Alert]:
    stmt = (
        select(Alert)
        .where(Alert.car_id == car_id)
        .order_by(desc(Alert.timestamp))
    )

    if unread_only:
        stmt = stmt.where(Alert.is_read == False)

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_alert_by_id(db: AsyncSession, alert_id: int) -> Alert | None:
    stmt = select(Alert).where(Alert.id == alert_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def mark_as_read(db: AsyncSession, alert_id: int) -> Alert | None:
    db_alert = await get_alert_by_id(db, alert_id)
    if not db_alert:
        return None

    db_alert.is_read = True
    await db.commit()
    await db.refresh(db_alert)
    return db_alert


async def mark_all_as_read(db: AsyncSession, car_id: int) -> int:
    stmt = (
        update(Alert)
        .where(Alert.car_id == car_id, Alert.is_read == False)
        .values(is_read=True)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount


async def delete_alert(db: AsyncSession, alert_id: int) -> Alert | None:
    db_alert = await get_alert_by_id(db, alert_id)
    if not db_alert:
        return None

    await db.delete(db_alert)
    await db.commit()
    return db_alert
