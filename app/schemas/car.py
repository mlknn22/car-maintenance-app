from pydantic import BaseModel

class CarBase(BaseModel):
    brand: str
    model: str
    year: int
    mileage: int

class CarCreate(CarBase):
    pass

class CarResponse(CarBase):
    id: int