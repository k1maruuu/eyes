from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

try:
    from sqlalchemy.dialects.postgresql import JSONB as JSONType
except Exception:
    from sqlalchemy import JSON as JSONType  # type: ignore

from src.db.base import Base


class OperationLog(Base):
    __tablename__ = "operation_log"
    __table_args__ = (UniqueConstraint("op_id", name="uq_operation_log_op_id"),)

    id = Column(Integer, primary_key=True, index=True)

    op_id = Column(String(64), nullable=False, index=True)
    action = Column(String(64), nullable=False, index=True)
    payload = Column(JSONType, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="ops")