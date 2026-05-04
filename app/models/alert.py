from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(
        Integer,
        ForeignKey("cars.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type = Column(String, nullable=False)
    message = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    car = relationship("Car", back_populates="alerts")
