from fastapi import FastAPI
from app.routes import cars, devices, maintenance_records, telemetry_logs, alerts
from app.models import car, device, maintenance_record, telemetry_log, alert, user

app = FastAPI(title="Car Maintenance API")


@app.get("/")
async def root():
    return {"message": "Car Maintenance App"}


app.include_router(cars.router)
app.include_router(devices.router)
app.include_router(maintenance_records.router)
app.include_router(telemetry_logs.router)
app.include_router(alerts.router)
