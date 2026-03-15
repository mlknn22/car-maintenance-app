from sqlalchemy.orm import Session
from app.models.device import Device
from app.schemas.device import DeviceCreate


def create_device(db: Session, device: DeviceCreate):

    db_device = Device(
        car_id=device.car_id,
        device_name=device.device_name
    )

    db.add(db_device)
    db.commit()
    db.refresh(db_device)

    return db_device


def get_devices(db: Session):

    return db.query(Device).all()