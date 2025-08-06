from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column, relationship

from src.models.base import Base


class ComputerAssignment(Base):
    __tablename__ = "computer_assignments"

    assignment_id = Column(Integer, primary_key=True)
    computer_id = mapped_column(ForeignKey("computers.computer_id"), nullable=False, unique=True)
    dept_id = mapped_column(ForeignKey("departments.dept_id"), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True))
    doc_number = Column(String, nullable=False)
    doc_date = Column(DateTime(timezone=True), nullable=False)
    doc_type = Column(String, nullable=False)

    computer = relationship("Computer", back_populates="assignment", foreign_keys=[computer_id])
    department = relationship("Department", back_populates="assignments", foreign_keys=[dept_id])
