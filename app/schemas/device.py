from pydantic import BaseModel
from datetime import datetime


class DeviceBase(BaseModel):
    model_config = {"extra": "forbid"}

    car_id: int
    device_name: str


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    model_config = {"extra": "forbid"}

    device_name: str | None = None
    connected: bool | None = None


class DeviceResponse(DeviceBase):
    id: int
    connected: bool
    last_seen: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True, "extra": "forbid"}