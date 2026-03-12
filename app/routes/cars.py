from fastapi import APIRouter

router = APIRouter()

@router.get("/cars")
async def get_cars():
    return [
        {"id": 1, "brand": "Toyota", "model": "Camry"},
        {"id": 2, "brand": "BMW", "model": "X5"}
    ]