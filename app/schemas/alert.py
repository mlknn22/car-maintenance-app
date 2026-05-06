from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal


class AlertBase(BaseModel):
    model_config = {"extra": "forbid"}

    car_id: int = Field(..., gt=0)
    type: str
    message: str
    severity: Literal["info", "warning", "critical"]


class AlertCreate(AlertBase):
    pass


class AlertResponse(AlertBase):
    id: int
    is_read: bool
    timestamp: datetime

    model_config = {"from_attributes": True, "extra": "forbid"}
