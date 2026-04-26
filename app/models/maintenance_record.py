from sqlalchemy import Column, String, Integer, Float, Date, ForeignKey
from sqlalchemy import func
from sqlalchemy import DateTime
from app.db.database import Base


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"


    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    service_date = Column(Date, nullable=False)
    work_type = Column(String, nullable=False)
    cost = Column(Float, nullable=False)
    mileage_at_service = Column(Integer, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) #сервер сам ставит время
