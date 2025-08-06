from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import mapped_column, relationship

from src.models.base import Base


class License(Base):
    __tablename__ = "licenses"

    license_id = Column(Integer, primary_key=True)
    software_id = mapped_column(ForeignKey("software.software_id"), nullable=False)
    vendor_id = mapped_column(ForeignKey("vendors.vendor_id"), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    price_per_unit = Column(Float, nullable=False)

    software = relationship("Software", back_populates="licenses", foreign_keys=[software_id])
    vendor = relationship("Vendor", back_populates="licenses", foreign_keys=[vendor_id])
    installations = relationship("Installation", cascade="all,delete", back_populates="license")
