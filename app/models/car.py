from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    mileage = Column(Integer, nullable=False)
    body_type = Column(String, nullable=False, server_default="Car")
    fuel_type = Column(String, nullable=False, server_default="Petrol")
    transmission = Column(String, nullable=False, server_default="Automatic")
    engine_size = Column(Integer, nullable=False, server_default="2000")
    brake_condition = Column(String, nullable=False, server_default="Good")
    owner_type = Column(String, nullable=False, server_default="First")
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    risk_score = Column(Float, nullable=True)

    user = relationship("User", back_populates="cars")
    devices = relationship(
        "Device",
        back_populates="car",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    alerts = relationship(
        "Alert",
        back_populates="car",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    maintenance_records = relationship(
        "MaintenanceRecord",
        back_populates="car",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
