from fastapi import FastAPI
from app.routes import cars

app = FastAPI(
    title="Car Maintenance API"
)

@app.get("/")
async def root():
    return {"message": "Car Maintenance App"}

app.include_router(cars.router)