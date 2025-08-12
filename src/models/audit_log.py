
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.sql import func

from src.models.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id = Column(Integer, primary_key=True)
    user_id = mapped_column(ForeignKey("users.user_id"), nullable=False)
    action = Column(String, nullable=False)
    action_time = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    user = relationship("User", back_populates="audit_logs", foreign_keys=[user_id])
