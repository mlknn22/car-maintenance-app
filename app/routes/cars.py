from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.car import CarCreate, CarResponse
from app.db.session import get_db
from app.crud.car import (
    create_car,
    get_cars,
    get_car_by_id,
    update_car,
    delete_car
)


router = APIRouter()


@router.post("/cars", response_model=CarResponse)
async def create_car_endpoint(car: CarCreate, db: Session = Depends(get_db)):
    return create_car(db, car)


@router.get("/cars", response_model=list[CarResponse])
async def get_cars_endpoint(db: Session = Depends(get_db)):
    return get_cars(db)


@router.get("/cars/{car_id}", response_model=CarResponse)
async def get_car_endpoint(car_id: int, db: Session = Depends(get_db)):
    car = get_car_by_id(db, car_id)

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    return car


@router.put("/cars/{car_id}", response_model=CarResponse)
async def update_car_endpoint(
    car_id: int,
    car: CarCreate,
    db: Session = Depends(get_db)
):

    updated_car = update_car(db, car_id, car)

    if not updated_car:
        raise HTTPException(status_code=404, detail="Car not found")

    return updated_car


@router.delete("/cars/{car_id}")
async def delete_car_endpoint(car_id: int, db: Session = Depends(get_db)):

    deleted_car = delete_car(db, car_id)

    if not deleted_car:
        raise HTTPException(status_code=404, detail="Car not found")

    return {"message": "Car deleted successfully"}