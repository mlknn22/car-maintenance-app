from sqlalchemy.orm import Session

from app.models.maintenance_record import MaintenanceRecord
from app.schemas.maintenance_record import MaintenanceRecordCreate, MaintenanceRecordUpdate


def create_maintenance_record(
    db: Session,
    record: MaintenanceRecordCreate
) -> MaintenanceRecord:
    db_record = MaintenanceRecord(**record.model_dump())

    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return db_record


def get_maintenance_records_by_car(
    db: Session,
    car_id: int,
    skip: int = 0,
    limit: int = 100
) -> list[MaintenanceRecord]:
    return (
        db.query(MaintenanceRecord)
        .filter(MaintenanceRecord.car_id == car_id)
        .order_by(MaintenanceRecord.service_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_maintenance_record_by_id(
    db: Session,
    record_id: int
) -> MaintenanceRecord | None:
    return (
        db.query(MaintenanceRecord)
        .filter(MaintenanceRecord.id == record_id)
        .first()
    )


def update_maintenance_record(
    db: Session,
    record_id: int,
    record_data: MaintenanceRecordUpdate
) -> MaintenanceRecord | None:
    db_record = get_maintenance_record_by_id(db, record_id)

    if not db_record:
        return None


    update_data = record_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_record, field, value)

    db.commit()
    db.refresh(db_record)

    return db_record


def delete_maintenance_record(
    db: Session,
    record_id: int
) -> MaintenanceRecord | None:
    db_record = get_maintenance_record_by_id(db, record_id)

    if not db_record:
        return None

    db.delete(db_record)
    db.commit()


    return db_record