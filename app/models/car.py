from sqlalchemy import Column, Integer, String
from app.db.database import Base

class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key = True, index=True)

    brand = Column(String, nullable = False)
    model = Column(String, nullable = False)

    year = Column(Integer, nullable = False)
    mileage = Column(Integer, nullable = False)
