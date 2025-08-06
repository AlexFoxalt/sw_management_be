from sqlalchemy import Column, DateTime, Enum, Integer, String
from sqlalchemy.orm import relationship

from src.enums import ComputerType
from src.models.base import Base


class Computer(Base):
    __tablename__ = "computers"

    computer_id = Column(Integer, primary_key=True)
    inventory_number = Column(String, nullable=False, unique=True)
    computer_type = Column(Enum(ComputerType), nullable=False)
    purchase_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, nullable=False, default="active")

    installations = relationship("Installation", cascade="all,delete", back_populates="computer")
    assignment = relationship("ComputerAssignment", cascade="all,delete", back_populates="computer")
