from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.crud.car import get_car_by_id
from app.crud.device import (
    create_device,
    delete_device,
    get_device_by_id,
    get_devices,
    get_devices_by_car,
    regenerate_device_token,
    update_device,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.device import (
    DeviceCreate,
    DeviceCreatedResponse,
    DeviceResponse,
    DeviceTokenResponse,
    DeviceUpdate,
)


router = APIRouter(prefix="/devices", tags=["Devices"])


@router.post("/", response_model=DeviceCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_device_endpoint(
    device: DeviceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await create_device(db, device, user_id=current_user.id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with id {device.car_id} not found",
        )
    db_device, plaintext_token = result
    return DeviceCreatedResponse(
        id=db_device.id,
        car_id=db_device.car_id,
        device_name=db_device.device_name,
        connected=db_device.connected,
        last_seen=db_device.last_seen,
        created_at=db_device.created_at,
        api_token=plaintext_token,
    )


@router.post(
    "/{device_id}/regenerate-token",
    response_model=DeviceTokenResponse,
)
async def regenerate_token_endpoint(
    device_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plaintext = await regenerate_device_token(db, device_id, user_id=current_user.id)
    if plaintext is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {device_id} not found",
        )
    return DeviceTokenResponse(api_token=plaintext)


@router.get("/", response_model=list[DeviceResponse])
async def get_devices_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_devices(db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/car/{car_id}", response_model=list[DeviceResponse])
async def get_devices_by_car_endpoint(
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
    return await get_devices_by_car(db, car_id, user_id=current_user.id)


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device_endpoint(
    device_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    device = await get_device_by_id(db, device_id, user_id=current_user.id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {device_id} not found",
        )
    return device


@router.patch("/{device_id}", response_model=DeviceResponse)
async def update_device_endpoint(
    device_data: DeviceUpdate,
    device_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updated = await update_device(db, device_id, device_data, user_id=current_user.id)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {device_id} not found",
        )
    return updated


@router.delete("/{device_id}", status_code=status.HTTP_200_OK)
async def delete_device_endpoint(
    device_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = await delete_device(db, device_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {device_id} not found",
        )
    return {"message": f"Device {device_id} deleted successfully"}
