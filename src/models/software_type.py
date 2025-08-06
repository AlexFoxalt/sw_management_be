from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.models.base import Base


class SoftwareType(Base):
    __tablename__ = "software_types"

    sw_type_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    software = relationship("Software", cascade="all,delete", back_populates="sw_type")
