from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.device import DeviceCreate, DeviceResponse
from app.db.session import get_db
from app.crud.device import create_device, get_devices


router = APIRouter(
    prefix="/devices",
    tags=["Devices"]
)


@router.post("/", response_model=DeviceResponse)
async def create_device_endpoint(device: DeviceCreate, db: Session = Depends(get_db)):

    return create_device(db, device)


@router.get("/", response_model=list[DeviceResponse])
async def get_devices_endpoint(db: Session = Depends(get_db)):

    return get_devices(db)