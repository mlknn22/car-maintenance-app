from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate


async def create_device(db: AsyncSession, device: DeviceCreate) -> Device:
    db_device = Device(**device.model_dump())
    db.add(db_device)
    await db.commit()
    await db.refresh(db_device)
    return db_device


async def get_devices(db: AsyncSession) -> list[Device]:
    stmt = select(Device)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_device_by_id(db: AsyncSession, device_id: int) -> Device | None:
    stmt = select(Device).where(Device.id == device_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_devices_by_car(db: AsyncSession, car_id: int) -> list[Device]:
    stmt = select(Device).where(Device.car_id == car_id)
    result = await db.execute(stmt)
    return result.scalars().all()


async def update_device(db: AsyncSession, device_id: int, device_data: DeviceUpdate) -> Device | None:
    db_device = await get_device_by_id(db, device_id)
    if not db_device:
        return None

    update_data = device_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_device, field, value)

    await db.commit()
    await db.refresh(db_device)
    return db_device


async def delete_device(db: AsyncSession, device_id: int) -> Device | None:
    db_device = await get_device_by_id(db, device_id)
    if not db_device:
        return None

    await db.delete(db_device)
    await db.commit()
    return db_device
