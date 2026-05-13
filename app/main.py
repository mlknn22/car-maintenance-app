from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.ml.predict import load_model
from app.models import alert, car, device, maintenance_record, telemetry_log, user
from app.routes import alerts, auth, cars, devices, maintenance_records, telemetry_logs


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    yield


app = FastAPI(title="Car Maintenance API", lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Car Maintenance App"}


app.include_router(auth.router)
app.include_router(cars.router)
app.include_router(devices.router)
app.include_router(maintenance_records.router)
app.include_router(telemetry_logs.router)
app.include_router(alerts.router)
