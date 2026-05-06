from pydantic import BaseModel, Field
from datetime import datetime


class TelemetryLogCreate(BaseModel):
    model_config = {"extra": "forbid"}

    device_id: int = Field(..., gt=0)

    coolant_temp: float | None = Field(
        None,
        ge=-40,
        le=200,
        description="Температура охлаждающей жидкости в градусах Цельсия"
    )

    rpm: float | None = Field(
        None,
        ge=0,
        le=10000,
        description="Обороты двигателя в RPM"
    )

    battery_voltage: float | None = Field(
        None,
        ge=0,
        le=20,
        description="Напряжение аккумулятора в вольтах"
    )


class TelemetryLogResponse(TelemetryLogCreate):
    id: int
    timestamp: datetime

    model_config = {"from_attributes": True, "extra": "forbid"}