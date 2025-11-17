"""
Schemas para Abastecimento (Refuel)
"""
from datetime import date, time, datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


class RefuelBase(BaseModel):
    """Schema base para abastecimento"""
    data: date = Field(..., description="Data do abastecimento")
    hora: time = Field(..., description="Hora do abastecimento")
    km: int = Field(..., gt=0, description="Quilometragem atual no odômetro")
    litros: Decimal = Field(..., gt=0, decimal_places=2, description="Quantidade de litros abastecidos")
    tipo_combustivel: Optional[str] = Field(None, max_length=50, description="Tipo de combustível (gasolina, diesel, etanol)")
    valor_litro: Decimal = Field(..., gt=0, decimal_places=2, description="Valor por litro")
    posto: Optional[str] = Field(None, max_length=100, description="Nome do posto")
    tanque_cheio: Optional[bool] = Field(False, description="Se o tanque foi completado")
    media: Optional[Decimal] = Field(None, decimal_places=2, description="Média km/L (calculado se tanque cheio)")


class RefuelCreate(RefuelBase):
    """Schema para criação de abastecimento (enviado ao Pub/Sub)"""
    id_usuario: UUID = Field(..., description="ID do usuário que registrou")
    placa: str = Field(..., min_length=7, max_length=10, description="Placa do veículo")


class RefuelResponse(BaseModel):
    """Schema para resposta com dados do abastecimento"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="ID único do abastecimento")
    data: date = Field(..., description="Data do abastecimento")
    hora: time = Field(..., description="Hora do abastecimento")
    km: int = Field(..., description="Quilometragem atual no odômetro")
    litros: Decimal = Field(..., description="Quantidade de litros abastecidos")
    tipo_combustivel: Optional[str] = Field(None, description="Tipo de combustível (gasolina, diesel, etanol)")
    valor_litro: Decimal = Field(..., description="Valor por litro")
    posto: Optional[str] = Field(None, description="Nome do posto")
    tanque_cheio: Optional[bool] = Field(False, description="Se o tanque foi completado")
    media: Optional[Decimal] = Field(None, description="Média km/L (calculado se tanque cheio)")
    valor_total: Decimal = Field(..., description="Valor total (litros * valor_litro)")
    id_usuario: Optional[UUID] = Field(None, description="ID do usuário que registrou")
    placa: str = Field(..., description="Placa do veículo")
    created_at: Optional[datetime] = Field(None, description="Data de criação do registro")
    updated_at: Optional[datetime] = Field(None, description="Data da última atualização")


class RefuelListResponse(BaseModel):
    """Schema para resposta de lista de abastecimentos"""
    refuels: list[RefuelResponse]
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    per_page: int = Field(..., description="Registros por página")


class RefuelUpdate(BaseModel):
    """Schema para atualização de abastecimento (todos campos opcionais)"""
    data: Optional[date] = None
    hora: Optional[time] = None
    km: Optional[int] = Field(None, gt=0)
    litros: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    tipo_combustivel: Optional[str] = Field(None, max_length=50)
    valor_litro: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    posto: Optional[str] = Field(None, max_length=100)
    tanque_cheio: Optional[bool] = None
    media: Optional[Decimal] = Field(None, decimal_places=2)


class RefuelPublishResponse(BaseModel):
    """Schema para resposta de publicação no Pub/Sub"""
    message: str = Field(..., description="Mensagem de sucesso")
    message_id: str = Field(..., description="ID da mensagem no Pub/Sub")
    status: str = Field(default="queued", description="Status do processamento")
