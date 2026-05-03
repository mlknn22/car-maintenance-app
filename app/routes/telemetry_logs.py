from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.schemas.telemetry_log import TelemetryLogResponse, TelemetryLogCreate
from app.db.session import get_db
from app.crud.telemetry_log import (
    create_telemetry_log,
    get_telemetry_logs_by_device,
    get_telemetry_logs_by_car,
    get_latest_telemetry_by_car,
)
from app.crud.device import get_device_by_id


router = APIRouter(prefix="/telemetry-logs", tags=["Telemetry Logs"])


@router.post("/", response_model=TelemetryLogResponse, status_code=status.HTTP_201_CREATED)
async def create_log(log: TelemetryLogCreate, db: AsyncSession = Depends(get_db)):
    device = await get_device_by_id(db, log.device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {log.device_id} not found"
        )

    device.last_seen = datetime.now(timezone.utc)
    await db.commit()

    return await create_telemetry_log(db, log)


@router.get("/", response_model=list[TelemetryLogResponse])
async def get_logs_by_device(
    device_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    device = await get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {device_id} not found"
        )
    return await get_telemetry_logs_by_device(db, device_id, skip=skip, limit=limit)


@router.get("/car/{car_id}/latest", response_model=TelemetryLogResponse)
async def get_latest_log_by_car(car_id: int, db: AsyncSession = Depends(get_db)):
    log = await get_latest_telemetry_by_car(db, car_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No telemetry data found for car {car_id}"
        )
    return log


@router.get("/car/{car_id}", response_model=list[TelemetryLogResponse])
async def get_logs_by_car(
    car_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await get_telemetry_logs_by_car(db, car_id, skip=skip, limit=limit)
