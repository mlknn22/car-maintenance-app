from fastapi import APIRouter, Depends, HTTPexception, status
from sqlalchemy.orm import Session

from app.schemas.telemetry_log import TelemetryLogResponse, TelemetryLogCreate
from app.db.session import get_db
from app.crud.telemetry_log import(
    create_telemetry_log,
    get_telemetry_logs_by_device,
    get_telemetry_logs_by_car,
    get_latest_telemetry_by_car
)


router = APIRouter(prefix="/telemetry_logs", tags=["Telemetry Logs"])


@router.post("/", response_model=TelemetryLogResponse):
async def create_log(log: TelemetryLogCreate, db: Session = Depends(get_db), status_code=status.HTTP_201_CREATED):
    return create_telemetry_log(db, log)