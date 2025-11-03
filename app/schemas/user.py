from datetime import datetime
from typing import Optional
from uuid import UUID as UuidType

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from .enums import UserStatus, UserType


class UserBase(BaseModel):
    """Schema base para usuário com campos comuns"""
    name: str = Field(..., min_length=1, max_length=100)
    lastName: str = Field(..., min_length=3, max_length=250)
    email: EmailStr = Field(..., description="Email único do usuário")
    cpf: str = Field(..., min_length=11, max_length=14, description="CPF do usuário")
    type: UserType = Field(..., description="Tipo do usuário")
    status: UserStatus = Field(default=UserStatus.PENDENTE, description="Status do usuário") 


class UserCreate(UserBase):
    """Schema para criação de usuário"""
    password: str = Field(..., min_length=8, description="Senha do usuário")

class UserUpdate(BaseModel):
    """Schema para atualização de usuário (todos os campos opcionais)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nome do usuário")
    lastName: Optional[str] = Field(None, min_length=3, max_length=250, description="Sobrenome do usuário")
    email: Optional[EmailStr] = Field(None, description="Email único do usuário")
    password: Optional[str] = Field(None, min_length=8, description="Senha do usuário")
    cpf: Optional[str] = Field(None, min_length=11, max_length=14, description="CPF do usuário")
    type: Optional[UserType] = Field(None, description="Tipo do usuário")
    status: Optional[UserStatus] = Field(None, description="Status do usuário")


class UserResponse(UserBase):
    """Schema para resposta com dados do usuário"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UuidType = Field(..., description="Identificador único do usuário")
    created_at: datetime = Field(..., description="Data e hora da criação")
    updated_at: Optional[datetime] = Field(None, description="Data e hora da última atualização")


class UserListResponse(BaseModel):
    """Schema para resposta de lista de usuários"""
    users: list[UserResponse]
    total: int = Field(..., description="Número total de usuários")
    page: int = Field(..., description="Página atual")
    per_page: int = Field(..., description="Usuários por página")