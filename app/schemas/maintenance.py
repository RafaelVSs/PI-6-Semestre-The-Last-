from datetime import datetime
from typing import Optional
from uuid import UUID as UuidType

from pydantic import BaseModel, Field, ConfigDict

from .enums import MaintenanceStatus


class MaintenanceItemsBase(BaseModel):
    """Schema para itens de manutenção"""
    oleo: bool = Field(default=False, description="Troca de óleo")
    filtro_oleo: bool = Field(default=False, description="Troca de filtro de óleo")
    filtro_combustivel: bool = Field(default=False, description="Troca de filtro de combustível")
    filtro_ar: bool = Field(default=False, description="Troca de filtro de ar")
    engraxamento: bool = Field(default=False, description="Engraxamento")


class MaintenanceBase(BaseModel):
    """Schema base para manutenção com campos comuns"""
    placa: str = Field(..., min_length=7, max_length=10, description="Placa do veículo")
    km_atual: int = Field(..., ge=0, description="Quilometragem atual no momento da manutenção")
    oleo: bool = Field(default=False, description="Troca de óleo")
    filtro_oleo: bool = Field(default=False, description="Troca de filtro de óleo")
    filtro_combustivel: bool = Field(default=False, description="Troca de filtro de combustível")
    filtro_ar: bool = Field(default=False, description="Troca de filtro de ar")
    engraxamento: bool = Field(default=False, description="Engraxamento")
    status: MaintenanceStatus = Field(default=MaintenanceStatus.PENDENTE, description="Status da manutenção")


class MaintenanceCreate(MaintenanceBase):
    """Schema para criação de manutenção"""
    pass


class MaintenanceUpdate(BaseModel):
    """Schema para atualização de manutenção (todos os campos opcionais)"""
    km_atual: Optional[int] = Field(None, ge=0, description="Quilometragem atual")
    oleo: Optional[bool] = Field(None, description="Troca de óleo")
    filtro_oleo: Optional[bool] = Field(None, description="Troca de filtro de óleo")
    filtro_combustivel: Optional[bool] = Field(None, description="Troca de filtro de combustível")
    filtro_ar: Optional[bool] = Field(None, description="Troca de filtro de ar")
    engraxamento: Optional[bool] = Field(None, description="Engraxamento")
    status: Optional[MaintenanceStatus] = Field(None, description="Status da manutenção")


class MaintenanceResponse(MaintenanceBase):
    """Schema para resposta com dados da manutenção"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UuidType = Field(..., description="Identificador único da manutenção")
    created_at: datetime = Field(..., description="Data e hora da criação (data da manutenção)")
    updated_at: Optional[datetime] = Field(None, description="Data e hora da última atualização")
    
    # Objeto de itens para facilitar uso no frontend
    @property
    def manutencoes(self) -> dict:
        """Retorna itens de manutenção agrupados"""
        return {
            "oleo": self.oleo,
            "filtroOleo": self.filtro_oleo,
            "filtroCombustivel": self.filtro_combustivel,
            "filtroAr": self.filtro_ar,
            "engraxamento": self.engraxamento
        }
    
    @property
    def data(self) -> str:
        """Retorna data formatada"""
        return self.created_at.isoformat()


class MaintenanceListResponse(BaseModel):
    """Schema para resposta de lista de manutenções"""
    maintenances: list[MaintenanceResponse]
    total: int = Field(..., description="Número total de manutenções")
    page: int = Field(..., description="Página atual")
    per_page: int = Field(..., description="Manutenções por página")
