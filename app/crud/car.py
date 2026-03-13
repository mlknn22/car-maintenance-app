from sqlalchemy.orm import Session
from app.models.car import Car
from app.schemas.car import CarCreate


def create_car(db: Session, car: CarCreate):

    db_car = Car(
        brand=car.brand,
        model=car.model,
        year=car.year,
        mileage=car.mileage
    )

    db.add(db_car)
    db.commit()
    db.refresh(db_car)

    return db_car


def get_cars(db: Session):

    return db.query(Car).all()