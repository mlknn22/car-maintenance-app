from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.crud.car import get_car_by_id
from app.crud.device import get_device_by_id
from app.crud.telemetry_log import (
    create_telemetry_log,
    get_latest_telemetry_by_car,
    get_telemetry_logs_by_car,
    get_telemetry_logs_by_device,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.telemetry_log import TelemetryLogCreate, TelemetryLogResponse


router = APIRouter(prefix="/telemetry-logs", tags=["Telemetry Logs"])


@router.post("/", response_model=TelemetryLogResponse, status_code=status.HTTP_201_CREATED)
async def create_log(
    log: TelemetryLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    device = await get_device_by_id(db, log.device_id, user_id=current_user.id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {log.device_id} not found",
        )

    device.last_seen = datetime.now(timezone.utc)
    await db.commit()

    return await create_telemetry_log(db, log, user_id=current_user.id)


@router.get("/", response_model=list[TelemetryLogResponse])
async def get_logs_by_device(
    device_id: int = Query(..., gt=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    device = await get_device_by_id(db, device_id, user_id=current_user.id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {device_id} not found",
        )
    return await get_telemetry_logs_by_device(
        db, device_id, user_id=current_user.id, skip=skip, limit=limit
    )


@router.get("/car/{car_id}/latest", response_model=TelemetryLogResponse)
async def get_latest_log_by_car(
    car_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    car = await get_car_by_id(db, car_id, user_id=current_user.id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with id {car_id} not found",
        )
    log = await get_latest_telemetry_by_car(db, car_id, user_id=current_user.id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No telemetry data found for car {car_id}",
        )
    return log


@router.get("/car/{car_id}", response_model=list[TelemetryLogResponse])
async def get_logs_by_car(
    car_id: int = Path(..., gt=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    car = await get_car_by_id(db, car_id, user_id=current_user.id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with id {car_id} not found",
        )
    return await get_telemetry_logs_by_car(
        db, car_id, user_id=current_user.id, skip=skip, limit=limit
    )
