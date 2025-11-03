from datetime import datetime
from typing import Optional
from uuid import UUID as UuidType

from pydantic import BaseModel, Field, ConfigDict

from .enums import VehicleType


class VehicleBase(BaseModel):
    """Schema base para veículo com campos comuns"""
    placa: str = Field(..., min_length=7, max_length=10, description="Placa do veículo")
    modelo: str = Field(..., min_length=1, max_length=100, description="Modelo do veículo")
    marca: str = Field(..., min_length=1, max_length=100, description="Marca do veículo")
    ano: int = Field(..., ge=1900, le=2100, description="Ano do veículo")
    tipo: VehicleType = Field(..., description="Tipo do veículo (carro, caminhão, van)")
    frota: Optional[str] = Field(None, max_length=50, description="Identificação da frota")
    km_atual: int = Field(default=0, ge=0, description="Quilometragem atual do veículo")
    frequencia_km_manutencao: Optional[int] = Field(None, gt=0, description="Frequência de manutenção em km")
    km_prox_manutencao: Optional[int] = Field(None, ge=0, description="KM da próxima manutenção")
    capacidade_tanque: int = Field(..., gt=0, description="Capacidade do tanque em litros")
    km_ultimo_abastecimento: Optional[int] = Field(None, ge=0, description="KM do último abastecimento")


class VehicleCreate(VehicleBase):
    """Schema para criação de veículo"""
    id_usuario: UuidType = Field(..., description="ID do usuário responsável pelo veículo")


class VehicleUpdate(BaseModel):
    """Schema para atualização de veículo (todos os campos opcionais)"""
    placa: Optional[str] = Field(None, min_length=7, max_length=10, description="Placa do veículo")
    modelo: Optional[str] = Field(None, min_length=1, max_length=100, description="Modelo do veículo")
    marca: Optional[str] = Field(None, min_length=1, max_length=100, description="Marca do veículo")
    ano: Optional[int] = Field(None, ge=1900, le=2100, description="Ano do veículo")
    tipo: Optional[VehicleType] = Field(None, description="Tipo do veículo")
    id_usuario: Optional[UuidType] = Field(None, description="ID do usuário responsável")
    frota: Optional[str] = Field(None, max_length=50, description="Identificação da frota")
    km_atual: Optional[int] = Field(None, ge=0, description="Quilometragem atual")
    frequencia_km_manutencao: Optional[int] = Field(None, gt=0, description="Frequência de manutenção")
    km_prox_manutencao: Optional[int] = Field(None, ge=0, description="KM da próxima manutenção")
    manutencao_vencida: Optional[bool] = Field(None, description="Flag de manutenção vencida")
    capacidade_tanque: Optional[int] = Field(None, gt=0, description="Capacidade do tanque")
    km_ultimo_abastecimento: Optional[int] = Field(None, ge=0, description="KM do último abastecimento")


class VehicleResponse(VehicleBase):
    """Schema para resposta com dados do veículo"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UuidType = Field(..., description="Identificador único do veículo")
    id_usuario: UuidType = Field(..., description="ID do usuário responsável")
    manutencao_vencida: bool = Field(..., description="Indica se a manutenção está vencida")
    created_at: datetime = Field(..., description="Data e hora da criação")
    updated_at: Optional[datetime] = Field(None, description="Data e hora da última atualização")


class VehicleListResponse(BaseModel):
    """Schema para resposta de lista de veículos"""
    vehicles: list[VehicleResponse]
    total: int = Field(..., description="Número total de veículos")
    page: int = Field(..., description="Página atual")
    per_page: int = Field(..., description="Veículos por página")
