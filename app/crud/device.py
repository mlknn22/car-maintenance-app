from sqlalchemy.orm import Session
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate


def create_device(db: Session, device: DeviceCreate) -> Device:
    db_device = Device(**device.model_dump())
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def get_devices(db: Session) -> list[Device]:
    return db.query(Device).all()


def get_device_by_id(db: Session, device_id: int) -> Device | None:
    return db.query(Device).filter(Device.id == device_id).first()


def get_devices_by_car(db: Session, car_id: int) -> list[Device]:
    return db.query(Device).filter(Device.car_id == car_id).all()


def update_device(db: Session, device_id: int, device_data: DeviceUpdate) -> Device | None:
    db_device = get_device_by_id(db, device_id)

    if not db_device:
        return None


    update_data = device_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_device, field, value)

    db.commit()
    db.refresh(db_device)
    return db_device


def delete_device(db: Session, device_id: int) -> Device | None:
    db_device = get_device_by_id(db, device_id)

    if not db_device:
        return None

    db.delete(db_device)
    db.commit()


    return db_device