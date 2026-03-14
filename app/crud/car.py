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

def get_car_by_id(db: Session, car_id: int):
    return db.query(Car).filter(Car.id == car_id).first()


def update_car(db: Session, car_id: int, car_data: CarCreate):
    car =  db.query(Car).filter(Car.id == car_id).first()

    if not car:
        return None
    
    car.brand = car_data.brand
    car.model = car_data.model
    car.mileage = car_data.mileage
    car.year = car_data.year

    db.commit()
    db.refresh(car)

    return car

def delete_car(db: Session, car_id: int):
    car =  db.query(Car).filter(Car.id == car_id).first()

    if not car:
        return None
    
    db.delete(car)
    db.commit()

    return car

