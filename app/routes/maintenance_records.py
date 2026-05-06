from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.crud.maintenance_record import (
    create_maintenance_record,
    delete_maintenance_record,
    get_maintenance_record_by_id,
    get_maintenance_records_by_car,
    update_maintenance_record,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.maintenance_record import (
    MaintenanceRecordCreate,
    MaintenanceRecordResponse,
    MaintenanceRecordUpdate,
)


router = APIRouter(prefix="/maintenance-records", tags=["Maintenance Records"])


@router.post("/", response_model=MaintenanceRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_record(
    record: MaintenanceRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_record = await create_maintenance_record(db, record, user_id=current_user.id)
    if db_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with id {record.car_id} not found",
        )
    return db_record


@router.get("/", response_model=list[MaintenanceRecordResponse])
async def get_records(
    car_id: int = Query(..., gt=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_maintenance_records_by_car(
        db, car_id, user_id=current_user.id, skip=skip, limit=limit
    )


@router.get("/{record_id}", response_model=MaintenanceRecordResponse)
async def get_record(
    record_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = await get_maintenance_record_by_id(db, record_id, user_id=current_user.id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Maintenance record with id {record_id} not found",
        )
    return record


@router.patch("/{record_id}", response_model=MaintenanceRecordResponse)
async def update_record(
    record_data: MaintenanceRecordUpdate,
    record_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updated = await update_maintenance_record(
        db, record_id, record_data, user_id=current_user.id
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Maintenance record with id {record_id} not found",
        )
    return updated


@router.delete("/{record_id}", status_code=status.HTTP_200_OK)
async def delete_record(
    record_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = await delete_maintenance_record(db, record_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Maintenance record with id {record_id} not found",
        )
    return {"message": f"Maintenance record {record_id} deleted successfully"}
