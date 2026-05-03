from sqlalchemy.ext.asyncio import AsyncSession
from app.models.car import Car
from app.schemas.car import CarCreate
from sqlalchemy import select

async def create_car(db: AsyncSession, car: CarCreate):

    db_car = Car(
        brand=car.brand,
        model=car.model,
        year=car.year,
        mileage=car.mileage
    )

    db.add(db_car)
    await db.commit()
    await db.refresh(db_car)

    return db_car

async def get_cars(db: AsyncSession):
    stmt = select(Car)
    result = await db.execute(stmt)
    cars = result.scalars().all()
    return cars

async def get_car_by_id(db: AsyncSession, car_id: int):
    stmt = select(Car).where(Car.id==car_id)
    result = await db.execute(stmt)
    car = result.scalar_one_or_none()
    return car

async def update_car(db: AsyncSession, car_id: int, car_data: CarCreate):
    stmt = select(Car).where(Car.id == car_id)
    result = await db.execute(stmt)
    car = result.scalar_one_or_none()

    if not car:
        return None

    car.brand = car_data.brand
    car.model = car_data.model
    car.mileage = car_data.mileage
    car.year = car_data.year

    await db.commit()
    await db.refresh(car)

    return car

async def delete_car(db: AsyncSession, car_id: int):
    stmt = select(Car).where(Car.id == car_id)
    result = await db.execute(stmt)
    car = result.scalar_one_or_none()

    if not car:
        return None

    await db.delete(car)
    await db.commit()

    return car

