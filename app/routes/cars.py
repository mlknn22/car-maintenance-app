from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.car import CarCreate, CarResponse
from app.db.session import get_db
from app.crud.car import create_car, get_cars

router = APIRouter()


@router.post("/cars", response_model=CarResponse)
async def create_car_endpoint(car: CarCreate, db: Session = Depends(get_db)):
    return create_car(db, car)


@router.get("/cars", response_model=list[CarResponse])
async def get_cars_endpoint(db: Session = Depends(get_db)):
    return get_cars(db)