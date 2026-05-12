from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class TelemetryLogCreate(BaseModel):
    model_config = {"extra": "forbid"}

    device_id: int = Field(..., gt=0)

    timestamp: datetime | None = Field(
        None,
        description=(
            "Опциональная UTC-метка времени лога. "
            "Если не задана — БД проставит server_default=now(). "
            "Должна быть timezone-aware (наивный datetime отклоняется). "
            "Используется симулятором для бэкфилла истории."
        ),
    )

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

    speed: float | None = Field(
        None,
        ge=0,
        le=300,
        description="Скорость автомобиля в км/ч"
    )

    engine_load: float | None = Field(
        None,
        ge=0,
        le=100,
        description="Расчётная нагрузка двигателя в процентах"
    )

    @field_validator("timestamp")
    @classmethod
    def _require_tz_aware(cls, v: datetime | None) -> datetime | None:
        if v is not None and v.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware (include tz offset)")
        return v


class TelemetryLogResponse(TelemetryLogCreate):
    id: int
    timestamp: datetime

    model_config = {"from_attributes": True, "extra": "forbid"}