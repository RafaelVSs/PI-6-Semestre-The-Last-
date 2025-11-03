from sqlalchemy import String, Integer, Numeric, Date, Time, Boolean, ForeignKey, Computed
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal
from datetime import date, time
from uuid import UUID as UuidType

from .base import BaseModel


class Refuel(BaseModel):
    """Modelo de Abastecimento"""
    __tablename__ = "refuel"
    
    data: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Data do abastecimento"
    )
    
    hora: Mapped[time] = mapped_column(
        Time,
        nullable=False,
        comment="Hora do abastecimento"
    )
    
    km: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Quilometragem no odômetro"
    )
    
    litros: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Quantidade de litros abastecidos"
    )
    
    tipo_combustivel: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Tipo de combustível (gasolina, diesel, etanol)"
    )
    
    valor_litro: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Valor por litro"
    )
    
    posto: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Nome do posto"
    )
    
    # Valor total calculado automaticamente pelo banco
    valor_total: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        Computed("litros * valor_litro"),
        nullable=False,
        comment="Valor total (calculado: litros * valor_litro)"
    )
    
    tanque_cheio: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        default=False,
        comment="Se o tanque foi completado"
    )
    
    media: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Média km/L (calculado apenas se tanque cheio)"
    )
    
    # Foreign Keys
    id_usuario: Mapped[UuidType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID do usuário que registrou"
    )
    
    placa: Mapped[str] = mapped_column(
        String(10),
        # ForeignKey("veiculo.placa", ondelete="CASCADE"),  # Descomente quando criar tabela veiculo
        nullable=False,
        index=True,
        comment="Placa do veículo"
    )
    
    # Relationships
    usuario: Mapped["User"] = relationship("User", back_populates="abastecimentos")
    # veiculo: Mapped["Veiculo"] = relationship("Veiculo", back_populates="abastecimentos")  # Descomente quando criar modelo Veiculo
    
    def __repr__(self) -> str:
        return f"<Refuel(id={self.id_abastecimento}, placa='{self.placa}', data='{self.data}', litros={self.litros})>"