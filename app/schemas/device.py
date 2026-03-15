from pydantic import BaseModel


class DeviceBase(BaseModel):
    car_id: int
    device_name: str


class DeviceCreate(DeviceBase):
    pass


class DeviceResponse(DeviceBase):
    id: int
    connected: bool