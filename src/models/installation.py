from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import mapped_column, relationship

from src.models.base import Base


class Installation(Base):
    __tablename__ = "installations"

    installation_id = Column(Integer, primary_key=True)
    computer_id = mapped_column(ForeignKey("computers.computer_id"), nullable=False)
    license_id = mapped_column(ForeignKey("licenses.license_id"), nullable=False)
    install_date = Column(DateTime(timezone=True), nullable=False)

    computer = relationship("Computer", back_populates="installations", foreign_keys=[computer_id])
    license = relationship("License", back_populates="installations", foreign_keys=[license_id])
