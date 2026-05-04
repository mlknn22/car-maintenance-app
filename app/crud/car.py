from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.car import Car
from app.schemas.car import CarCreate, CarUpdate


async def create_car(db: AsyncSession, car: CarCreate) -> Car:
    db_car = Car(**car.model_dump())
    db.add(db_car)
    await db.commit()
    await db.refresh(db_car)
    return db_car


async def get_cars(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Car]:
    stmt = select(Car).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_car_by_id(db: AsyncSession, car_id: int) -> Car | None:
    stmt = select(Car).where(Car.id == car_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_car(db: AsyncSession, car_id: int, car_data: CarUpdate) -> Car | None:
    car = await get_car_by_id(db, car_id)
    if not car:
        return None

    update_data = car_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(car, field, value)

    await db.commit()
    await db.refresh(car)
    return car


async def delete_car(db: AsyncSession, car_id: int) -> Car | None:
    car = await get_car_by_id(db, car_id)
    if not car:
        return None

    await db.delete(car)
    await db.commit()
    return car
