from fastapi import APIRouter
from app.schemas.car import CarCreate, CarResponse

router = APIRouter()

cars_db = []

@router.post("/cars", response_model=CarResponse)
async def create_car(car: CarCreate):
    car_dict = car.model_dump()
    car_dict["id"] = len(cars_db) + 1
    cars_db.append(car_dict)
    return car_dict

@router.get("/cars", response_model=list[CarResponse])
async def get_cars():
    return cars_db