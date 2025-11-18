from datetime import datetime
import uuid

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base  # <- IMPORT CORRETO


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_veiculo = Column(UUID(as_uuid=True), ForeignKey("veiculos.id"), nullable=False)
    id_abastecimento = Column(UUID(as_uuid=True), ForeignKey("refuel.id"), nullable=False)

    severity = Column(String(10), nullable=False)  # LOW, MEDIUM, HIGH
    message = Column(String(255), nullable=False)

    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    veiculo = relationship("Vehicle")
    abastecimento = relationship("Refuel")

