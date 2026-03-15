from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.db.database import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    device_name = Column(String, nullable=False)
    connected = Column(Boolean, default=True)