from pydantic import BaseModel, Field
from datetime import date, datetime

class MaintenanceRecordBase(BaseModel):
    car_id: int = Field(..., gt=0)
    service_date: date
    work_type: str = Field(..., min_length = 2)
    cost: float = Field(..., ge=0, description="Стоимость работ в рублях")
    mileage_at_service: int = Field(..., ge=0, description="Пробег автомобиля на момент проведения ТО в километрах")
    notes: str | None = None


class MaintenanceRecordCreate(MaintenanceRecordBase):
    pass


class MaintenanceRecordUpdate(BaseModel):
    service_date: date | None =  None
    work_type: str | None = Field(None, min_length = 2)
    cost: float | None = Field(None, ge=0)
    mileage_at_service: int | None = Field(None, ge=0)
    notes: str | None = None


class MaintenanceRecordResponse(MaintenanceRecordBase):
    id: int
    created_at: datetime


    model_config = {"from_attributes": True}


