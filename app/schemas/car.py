from pydantic import BaseModel, Field


class CarBase(BaseModel):
    model_config = {"extra": "forbid"}

    brand: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)
    year: int = Field(..., ge=1900, le=2100)
    mileage: int = Field(..., ge=0)


class CarCreate(CarBase):
    pass


class CarUpdate(BaseModel):
    model_config = {"extra": "forbid"}

    brand: str | None = Field(None, min_length=1)
    model: str | None = Field(None, min_length=1)
    year: int | None = Field(None, ge=1900, le=2100)
    mileage: int | None = Field(None, ge=0)


class CarResponse(CarBase):
    id: int
    user_id: int
    risk_score: float | None = None

    model_config = {"from_attributes": True, "extra": "forbid"}
