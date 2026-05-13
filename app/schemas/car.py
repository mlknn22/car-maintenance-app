from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

BodyType = Literal["Truck", "Van", "Bus", "Car", "Motorcycle", "SUV"]
FuelType = Literal["Electric", "Petrol", "Diesel"]
Transmission = Literal["Automatic", "Manual"]
BrakeCondition = Literal["New", "Good", "Worn Out"]
OwnerType = Literal["First", "Second", "Third"]


class CarBase(BaseModel):
    model_config = {"extra": "forbid"}

    brand: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)
    year: int = Field(..., ge=1900, le=2100)
    mileage: int = Field(..., ge=0)
    body_type: BodyType
    fuel_type: FuelType
    transmission: Transmission
    engine_size: int = Field(..., ge=600, le=8000)
    brake_condition: BrakeCondition
    owner_type: OwnerType


class CarCreate(CarBase):
    pass


class CarUpdate(BaseModel):
    model_config = {"extra": "forbid"}

    brand: str | None = Field(None, min_length=1)
    model: str | None = Field(None, min_length=1)
    year: int | None = Field(None, ge=1900, le=2100)
    mileage: int | None = Field(None, ge=0)
    body_type: BodyType | None = None
    fuel_type: FuelType | None = None
    transmission: Transmission | None = None
    engine_size: int | None = Field(None, ge=600, le=8000)
    brake_condition: BrakeCondition | None = None
    owner_type: OwnerType | None = None


class CarResponse(CarBase):
    id: int
    user_id: int
    risk_score: float | None = None

    model_config = {"from_attributes": True, "extra": "forbid"}


class RiskScoreResponse(BaseModel):
    model_config = {"extra": "forbid"}

    car_id: int
    risk_score: float = Field(..., ge=0.0, le=1.0)
    model_name: str
    computed_at: datetime
