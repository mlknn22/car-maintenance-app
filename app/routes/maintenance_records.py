from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.maintenance_record import (
    MaintenanceRecordCreate, MaintenanceRecordUpdate, MaintenanceRecordResponse
)
from app.db.session import get_db
from app.crud.maintenance_record import (
    create_maintenance_record,
    get_maintenance_records_by_car,
    get_maintenance_record_by_id,
    update_maintenance_record,
    delete_maintenance_record,
)

from app.crud.car import get_car_by_id


router = APIRouter(prefix="/maintenance-records", tags=["Maintenance Records"])


@router.post("/", response_model=MaintenanceRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_record(record: MaintenanceRecordCreate, db: AsyncSession = Depends(get_db)):
    car = await get_car_by_id(db, record.car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with id {record.car_id} not found"
        )

    return await create_maintenance_record(db, record)


@router.get("/", response_model=list[MaintenanceRecordResponse])
async def get_records(
        car_id: int,
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db),
):
    car = await get_car_by_id(db, car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with id {car_id} not found"
        )

    return await get_maintenance_records_by_car(db, car_id, skip=skip, limit=limit)


@router.get("/{record_id}", response_model=MaintenanceRecordResponse)
async def get_record(
        record_id: int,
        db: AsyncSession = Depends(get_db),
):
    record = await get_maintenance_record_by_id(db, record_id)

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Maintenance record with id {record_id} not found"
        )

    return record


@router.patch("/{record_id}", response_model=MaintenanceRecordResponse)
async def update_record(
        record_id: int,
        record_data: MaintenanceRecordUpdate,
        db: AsyncSession = Depends(get_db),
):
    updated = await update_maintenance_record(db, record_id, record_data)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Maintenance record with id {record_id} not found"
        )

    return updated


@router.delete("/{record_id}", status_code=status.HTTP_200_OK)
async def delete_record(
        record_id: int,
        db: AsyncSession = Depends(get_db),
):
    deleted = await delete_maintenance_record(db, record_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Maintenance record with id {record_id} not found"
        )

    return {"message": f"Maintenance record {record_id} deleted successfully"}
