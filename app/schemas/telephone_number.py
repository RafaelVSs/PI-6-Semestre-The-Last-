from datetime import datetime
from typing import Optional
from uuid import UUID as UuidType

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from .enums import TelephoneNumberStatus

class TelephoneNumberBase(BaseModel):
    id_user: UuidType = Field(...)
    number: str = Field(..., min_length=8, max_length=15)
    status: TelephoneNumberStatus = Field(default=TelephoneNumberStatus.ATIVO)

class TelephoneNumberCreate(TelephoneNumberBase):
    pass

class TelephoneNumberResponse(TelephoneNumberBase):
    """Schema para resposta com dados do número de telefone"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UuidType = Field(..., description="Identificador único do número de telefone")
    created_at: datetime = Field(..., description="Data e hora da criação")
    updated_at: Optional[datetime] = Field(None, description="Data e hora da última atualização")

class TelephoneNumberListResponse(BaseModel):
    """Schema para resposta de lista de números de telefone"""
    telephone_numbers: list[TelephoneNumberResponse]
    total: int = Field(..., description="Número total de números de telefone")
    page: int = Field(..., description="Página atual")
    per_page: int = Field(..., description="Números de telefone por página")

class TelephoneNumberUpdate(BaseModel):
    """Schema para atualização de número de telefone (todos os campos opcionais)"""
    number: Optional[str] = Field(None, min_length=8, max_length=15)
    status: Optional[TelephoneNumberStatus] = Field(None)            