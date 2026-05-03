from pydantic import BaseModel


class CarBase(BaseModel):
    brand: str
    model: str
    year: int
    mileage: int


class CarCreate(CarBase):
    pass


class CarUpdate(BaseModel):
    brand: str | None = None
    model: str | None = None
    year: int | None = None
    mileage: int | None = None


class CarResponse(CarBase):
    id: int
