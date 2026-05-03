from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.car import CarCreate, CarUpdate, CarResponse
from app.db.session import get_db
from app.crud.car import (
    create_car,
    get_cars,
    get_car_by_id,
    update_car,
    delete_car,
)


router = APIRouter(prefix="/cars", tags=["Cars"])


@router.post("/", response_model=CarResponse, status_code=status.HTTP_201_CREATED)
async def create_car_endpoint(car: CarCreate, db: AsyncSession = Depends(get_db)):
    return await create_car(db, car)


@router.get("/", response_model=list[CarResponse])
async def get_cars_endpoint(db: AsyncSession = Depends(get_db)):
    return await get_cars(db)


@router.get("/{car_id}", response_model=CarResponse)
async def get_car_endpoint(car_id: int, db: AsyncSession = Depends(get_db)):
    car = await get_car_by_id(db, car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


@router.patch("/{car_id}", response_model=CarResponse)
async def update_car_endpoint(
    car_id: int,
    car: CarUpdate,
    db: AsyncSession = Depends(get_db),
):
    updated_car = await update_car(db, car_id, car)
    if not updated_car:
        raise HTTPException(status_code=404, detail="Car not found")
    return updated_car


@router.delete("/{car_id}")
async def delete_car_endpoint(car_id: int, db: AsyncSession = Depends(get_db)):
    deleted_car = await delete_car(db, car_id)
    if not deleted_car:
        raise HTTPException(status_code=404, detail="Car not found")
    return {"message": "Car deleted successfully"}
