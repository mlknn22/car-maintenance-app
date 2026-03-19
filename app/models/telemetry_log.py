from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base


class TelemetryLog(Base):
    __tablename__ = "telemetry_logs"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    timestamp = Column(DateTime, server_default=func.now(), index=True)


    coolant_temp = Column(Float, nullable=True)
    rpm = Column(Float, nullable=True)
    battery_voltage = Column(Float, nullable=True)