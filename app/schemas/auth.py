from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Schema para requisição de login"""
    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., min_length=8, description="Senha do usuário")


class TokenResponse(BaseModel):
    """Schema para resposta com token JWT"""
    access_token: str = Field(..., description="Token de acesso JWT")
    token_type: str = Field(default="bearer", description="Tipo do token")
    expires_in: int = Field(..., description="Tempo de expiração em segundos")


class TokenData(BaseModel):
    """Schema para dados contidos no token JWT"""
    user_id: UUID = Field(..., description="ID do usuário")
    email: str = Field(..., description="Email do usuário")
    user_type: str = Field(..., description="Tipo do usuário")
    exp: Optional[datetime] = Field(None, description="Data de expiração do token")
