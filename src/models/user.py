from sqlalchemy import Column, Enum, Integer, String
from sqlalchemy.orm import relationship

from src.enums import UserRole
from src.models.base import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    full_name = Column(String, nullable=False)

    audit_logs = relationship("AuditLog", cascade="all,delete", back_populates="user")
