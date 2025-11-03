from datetime import datetime
from typing import Optional
from uuid import UUID as UuidType

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid_extensions import uuid7


class Base(DeclarativeBase):
    """Base class para todos os modelos SQLAlchemy"""
    pass


class BaseModel(Base):
    """
    Classe base com campos comuns para todos os modelos de banco de dados.
    Inclui ID único (UUID v7), timestamps de auditoria e métodos utilitários.
    """
    __abstract__ = True

    id: Mapped[UuidType] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid7,
        comment="Identificador único do registro"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Data e hora da criação do registro"
    )
    
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
        comment="Data e hora da última atualização do registro"
    )

    def __repr__(self) -> str:
        """Representação string básica do modelo"""
        return f"<{self.__class__.__name__}(id={self.id})>"