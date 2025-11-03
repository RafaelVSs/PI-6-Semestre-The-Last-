
from sqlalchemy import String, UniqueConstraint, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID as UuidType

from .base import BaseModel
from app.schemas.enums import TelephoneNumberStatus

class TelephoneNumber(BaseModel):
    __tablename__ = "telephone_numbers"
    
    id_user: Mapped[UuidType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    number: Mapped[str] = mapped_column(
        String(15),
        unique=True,
        nullable=False,
    )

    status: Mapped[TelephoneNumberStatus] = mapped_column(
        Enum(TelephoneNumberStatus),
        default=TelephoneNumberStatus.ATIVO,
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="telephone_numbers")

    __table_args__ = (
        UniqueConstraint('number', name='uq_telephone_number'),
    )

    def __repr__(self) -> str:
        return f"<TelephoneNumber(id={self.id}, number='{self.number}', status='{self.status}')>"