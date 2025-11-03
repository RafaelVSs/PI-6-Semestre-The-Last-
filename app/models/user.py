from sqlalchemy import String, UniqueConstraint, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from .base import BaseModel
from app.schemas.enums import UserStatus, UserType


class User(BaseModel):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    
    lastName: Mapped[str] = mapped_column(
        String(250),
        nullable=False,
    )
    
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    
    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    
    cpf: Mapped[str] = mapped_column(
        String(14),
        unique=True,
        nullable=False,
    )

    type: Mapped[UserType] = mapped_column(
        Enum(UserType),
        nullable=False,
    )
    
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus),
        default=UserStatus.PENDENTE,
        nullable=False,
    )

    # Relacionamento com TelephoneNumber
    telephone_numbers: Mapped[List["TelephoneNumber"]] = relationship(
        "TelephoneNumber",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"  # Mudado de "selectin" para "select" (lazy loading padrão)
    )
    
    # Relacionamento com Abastecimentos
    abastecimentos: Mapped[List["Refuel"]] = relationship(
        "Refuel",
        back_populates="usuario",
        lazy="select"
    )
    
    # Relacionamento com Veículos
    veiculos: Mapped[List["Vehicle"]] = relationship(
        "Vehicle",
        back_populates="usuario",
        cascade="all, delete-orphan",
        lazy="select"
    )

    __table_args__ = (
        UniqueConstraint('email', name='uq_user_email'),
        UniqueConstraint('cpf', name='uq_user_cpf'),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', type='{self.type}', status='{self.status}')>"