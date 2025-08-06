from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.models.base import Base


class Department(Base):
    __tablename__ = "departments"

    dept_id = Column(Integer, primary_key=True)
    dept_code = Column(String, nullable=False, unique=True)
    dept_name = Column(String, nullable=False)
    dept_short_name = Column(String)

    assignments = relationship(
        "ComputerAssignment", cascade="all,delete", back_populates="department"
    )
