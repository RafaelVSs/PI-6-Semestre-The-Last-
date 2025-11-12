from sqlalchemy import String, Integer, Boolean, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID

from .base import BaseModel
from app.schemas.enums import MaintenanceStatus


class Maintenance(BaseModel):
    __tablename__ = "manutencoes"

    placa: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("veiculos.placa", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    km_atual: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Quilometragem registrada no momento da manutenção"
    )
    
    # Itens de manutenção (checkboxes)
    oleo: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Troca de óleo"
    )
    
    filtro_oleo: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Troca de filtro de óleo"
    )
    
    filtro_combustivel: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Troca de filtro de combustível"
    )
    
    filtro_ar: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Troca de filtro de ar"
    )
    
    engraxamento: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Engraxamento"
    )
    
    status: Mapped[MaintenanceStatus] = mapped_column(
        Enum(MaintenanceStatus),
        default=MaintenanceStatus.PENDENTE,
        nullable=False,
        comment="Status da manutenção"
    )
    
    # Relacionamento com Vehicle
    veiculo: Mapped["Vehicle"] = relationship(
        "Vehicle",
        back_populates="manutencoes",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Maintenance(id={self.id}, placa='{self.placa}', km_atual={self.km_atual}, status='{self.status}')>"
