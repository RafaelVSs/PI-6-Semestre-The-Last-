"""
Router de autenticação - Login e geração de tokens JWT
"""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.db.client import get_db_session
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.user_service import UserService
from app.core.security import verify_password, create_access_token
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db_session)
) -> TokenResponse:
    """Endpoint de login"""
    service = UserService(db)
    
    # Buscar usuário por email (lança UserNotFoundError se não existir)
    user = await service.get_user_by_email(login_data.email)
    
    # Verificar senha com tratamento de erro
    try:
        password_valid = verify_password(login_data.password, user.password)
    except Exception:
        # Se houver erro na verificação (ex: formato inválido), considerar senha incorreta
        password_valid = False
    
    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar se usuário está ativo
    if user.status.value != "ativo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Usuário {user.status.value}. Entre em contato com o administrador.",
        )
    
    # Criar token JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),  # Subject: user ID
            "email": user.email,
            "type": user.type.value,
        },
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 600
    )
