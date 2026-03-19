from fastapi import FastAPI
from app.routes import (
    cars, devices, maintenance_records
)
from app.db.database import engine, Base
from app.models import car, device, maintenance_record

app = FastAPI(
    title="Car Maintenance API"
)

@app.get("/")
async def root():
    return {"message": "Car Maintenance App"}

app.include_router(cars.router)
app.include_router(devices.router)
app.include_router(maintenance_records.router)

Base.metadata.create_all(bind=engine)