from sqlalchemy import Column, String, Integer, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(
        Integer,
        ForeignKey("cars.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    service_date = Column(Date, nullable=False)
    work_type = Column(String, nullable=False)
    cost = Column(Float, nullable=False)
    mileage_at_service = Column(Integer, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    car = relationship("Car", back_populates="maintenance_records")
