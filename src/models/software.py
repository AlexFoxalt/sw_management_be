from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column, relationship

from src.models.base import Base


class Software(Base):
    __tablename__ = "software"

    software_id = Column(Integer, primary_key=True)
    sw_type_id = mapped_column(ForeignKey("software_types.sw_type_id"), nullable=False)
    code = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    short_name = Column(String)
    manufacturer = Column(String, nullable=False)

    licenses = relationship("License", cascade="all,delete", back_populates="software")
    sw_type = relationship("SoftwareType", back_populates="software", foreign_keys=[sw_type_id])
