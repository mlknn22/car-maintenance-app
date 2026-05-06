from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.crud.alert import (
    create_alert,
    delete_alert,
    get_alerts_by_car,
    mark_all_as_read,
    mark_as_read,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.alert import AlertCreate, AlertResponse


router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert_endpoint(
    alert: AlertCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_alert = await create_alert(db, alert, user_id=current_user.id)
    if db_alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with id {alert.car_id} not found",
        )
    return db_alert


@router.get("/", response_model=list[AlertResponse])
async def get_alerts(
    car_id: int = Query(..., gt=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    unread_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_alerts_by_car(
        db, car_id, user_id=current_user.id,
        skip=skip, limit=limit, unread_only=unread_only,
    )


@router.patch("/{alert_id}/read", response_model=AlertResponse)
async def mark_alert_as_read(
    alert_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alert = await mark_as_read(db, alert_id, user_id=current_user.id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id {alert_id} not found",
        )
    return alert


@router.post("/read-all", status_code=status.HTTP_200_OK)
async def mark_all_alerts_as_read(
    car_id: int = Query(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = await mark_all_as_read(db, car_id, user_id=current_user.id)
    return {"message": f"Marked {count} alerts as read"}


@router.delete("/{alert_id}", status_code=status.HTTP_200_OK)
async def delete_alert_endpoint(
    alert_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = await delete_alert(db, alert_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id {alert_id} not found",
        )
    return {"message": f"Alert {alert_id} deleted successfully"}
