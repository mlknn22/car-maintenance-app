from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.alert import AlertCreate, AlertUpdate, AlertResponse
from app.db.session import get_db
from app.crud.alert import (
    create_alert,
    get_alerts_by_car,
    get_alert_by_id,
    mark_as_read,
    mark_all_as_read,
    delete_alert,
)
from app.crud.car import get_car_by_id


router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert_endpoint(alert: AlertCreate, db: AsyncSession = Depends(get_db)):
    car = await get_car_by_id(db, alert.car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with id {alert.car_id} not found"
        )
    return await create_alert(db, alert)


@router.get("/", response_model=list[AlertResponse])
async def get_alerts(
    car_id: int,
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    car = await get_car_by_id(db, car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with id {car_id} not found"
        )
    return await get_alerts_by_car(db, car_id, skip=skip, limit=limit, unread_only=unread_only)


@router.patch("/{alert_id}/read", response_model=AlertResponse)
async def mark_alert_as_read(alert_id: int, db: AsyncSession = Depends(get_db)):
    alert = await mark_as_read(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id {alert_id} not found"
        )
    return alert


@router.post("/read-all", status_code=status.HTTP_200_OK)
async def mark_all_alerts_as_read(car_id: int, db: AsyncSession = Depends(get_db)):
    car = await get_car_by_id(db, car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with id {car_id} not found"
        )
    count = await mark_all_as_read(db, car_id)
    return {"message": f"Marked {count} alerts as read"}


@router.delete("/{alert_id}", status_code=status.HTTP_200_OK)
async def delete_alert_endpoint(alert_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await delete_alert(db, alert_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id {alert_id} not found"
        )
    return {"message": f"Alert {alert_id} deleted successfully"}
