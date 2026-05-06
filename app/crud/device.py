from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.car import Car
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate


async def _user_owns_car(db: AsyncSession, car_id: int, user_id: int) -> bool:
    stmt = select(Car.id).where(Car.id == car_id, Car.user_id == user_id)
    return (await db.execute(stmt)).scalar_one_or_none() is not None


async def create_device(
    db: AsyncSession,
    device: DeviceCreate,
    user_id: int,
) -> Device | None:
    if not await _user_owns_car(db, device.car_id, user_id):
        return None

    db_device = Device(**device.model_dump())
    db.add(db_device)
    await db.commit()
    await db.refresh(db_device)
    return db_device


async def get_devices(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[Device]:
    stmt = (
        select(Device)
        .join(Car, Device.car_id == Car.id)
        .where(Car.user_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_device_by_id(
    db: AsyncSession,
    device_id: int,
    user_id: int,
) -> Device | None:
    stmt = (
        select(Device)
        .join(Car, Device.car_id == Car.id)
        .where(Device.id == device_id, Car.user_id == user_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_devices_by_car(
    db: AsyncSession,
    car_id: int,
    user_id: int,
) -> list[Device]:
    stmt = (
        select(Device)
        .join(Car, Device.car_id == Car.id)
        .where(Device.car_id == car_id, Car.user_id == user_id)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def update_device(
    db: AsyncSession,
    device_id: int,
    device_data: DeviceUpdate,
    user_id: int,
) -> Device | None:
    db_device = await get_device_by_id(db, device_id, user_id)
    if not db_device:
        return None

    update_data = device_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_device, field, value)

    await db.commit()
    await db.refresh(db_device)
    return db_device


async def delete_device(
    db: AsyncSession,
    device_id: int,
    user_id: int,
) -> Device | None:
    db_device = await get_device_by_id(db, device_id, user_id)
    if not db_device:
        return None

    await db.delete(db_device)
    await db.commit()
    return db_device
