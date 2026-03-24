from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceResponse
from app.db.session import get_db
from app.crud.device import (
    create_device,
    get_devices,
    get_device_by_id,
    get_devices_by_car,
    update_device,
    delete_device
)
from app.crud.car import get_car_by_id


router = APIRouter(prefix="/devices", tags=["Devices"])


@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device_endpoint(device: DeviceCreate, db: Session = Depends(get_db)):
    car = get_car_by_id(db, device.car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with id {device.car_id} not found"
        )
    return create_device(db, device)


@router.get("/", response_model=list[DeviceResponse])
async def get_devices_endpoint(db: Session = Depends(get_db)):
    return get_devices(db)


@router.get("/car/{car_id}", response_model=list[DeviceResponse])
async def get_devices_by_car_endpoint(car_id: int, db: Session = Depends(get_db)):
    car = get_car_by_id(db, car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with id {car_id} not found"
        )
    return get_devices_by_car(db, car_id)


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device_endpoint(device_id: int, db: Session = Depends(get_db)):
    device = get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {device_id} not found"
        )
    return device


@router.patch("/{device_id}", response_model=DeviceResponse)
async def update_device_endpoint(
    device_id: int,
    device_data: DeviceUpdate,
    db: Session = Depends(get_db)
):
    updated = update_device(db, device_id, device_data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {device_id} not found"
        )
    return updated


@router.delete("/{device_id}", status_code=status.HTTP_200_OK)
async def delete_device_endpoint(device_id: int, db: Session = Depends(get_db)):
    deleted = delete_device(db, device_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {device_id} not found"
        )
    return {"message": f"Device {device_id} deleted successfully"}