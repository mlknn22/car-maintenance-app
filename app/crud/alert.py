from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertUpdate


def create_alert(db: Session, alert: AlertCreate) -> Alert:
    db_alert = Alert(**alert.model_dump())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


def get_alerts_by_car(
    db: Session,
    car_id: int,
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False
) -> list[Alert]:
    query = (
        db.query(Alert)
        .filter(Alert.car_id == car_id)
        .order_by(desc(Alert.timestamp))
    )


    if unread_only:
        query = query.filter(Alert.is_read == False)

    return query.offset(skip).limit(limit).all()


def get_alert_by_id(db: Session, alert_id: int) -> Alert | None:
    return db.query(Alert).filter(Alert.id == alert_id).first()


def mark_as_read(db: Session, alert_id: int) -> Alert | None:
    db_alert = get_alert_by_id(db, alert_id)

    if not db_alert:
        return None

    db_alert.is_read = True
    db.commit()
    db.refresh(db_alert)
    return db_alert


def mark_all_as_read(db: Session, car_id: int) -> int:
    updated_count = (
        db.query(Alert)
        .filter(Alert.car_id == car_id, Alert.is_read == False)
        .update({"is_read": True})
    )
    db.commit()
    return updated_count


def delete_alert(db: Session, alert_id: int) -> Alert | None:
    db_alert = get_alert_by_id(db, alert_id)

    if not db_alert:
        return None

    db.delete(db_alert)
    db.commit()
    return db_alert