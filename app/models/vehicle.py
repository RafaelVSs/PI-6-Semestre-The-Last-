from sqlalchemy import String, Integer, Boolean, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from uuid import UUID

from .base import BaseModel
from app.schemas.enums import VehicleType


class Vehicle(BaseModel):
    __tablename__ = "veiculos"

    placa: Mapped[str] = mapped_column(
        String(10),
        unique=True,
        nullable=False,
        index=True
    )
    
    modelo: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    
    marca: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    
    ano: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    
    tipo: Mapped[VehicleType] = mapped_column(
        Enum(VehicleType),
        nullable=False
    )
    
    id_usuario: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    frota: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    
    km_atual: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    
    frequencia_km_manutencao: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )
    
    km_prox_manutencao: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )
    
    manutencao_vencida: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    capacidade_tanque: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    
    km_ultimo_abastecimento: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    # Relacionamento com User
    usuario: Mapped["User"] = relationship(
        "User",
        back_populates="veiculos",
        lazy="select"
    )
    
    # Relacionamento com Maintenance
    manutencoes: Mapped[list["Maintenance"]] = relationship(
        "Maintenance",
        back_populates="veiculo",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Vehicle(id={self.id}, placa='{self.placa}', modelo='{self.modelo}')>"


    alerts = relationship("Alert", back_populates="veiculo")
