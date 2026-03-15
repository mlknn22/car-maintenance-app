from fastapi import FastAPI
from app.routes import cars
from app.routes import devices
from app.db.database import engine, Base
from app.models import car

app = FastAPI(
    title="Car Maintenance API"
)

@app.get("/")
async def root():
    return {"message": "Car Maintenance App"}

app.include_router(cars.router)
app.include_router(devices.router)
Base.metadata.create_all(bind=engine)