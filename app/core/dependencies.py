from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.db.client import get_db_session
from app.core.security import decode_access_token
from app.services.user_service import UserService
from app.models.user import User
from app.schemas.enums import UserType
from app.common.exceptions import UserNotFoundError


# HTTPBearer scheme - apenas token JWT no header Authorization
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
) -> User:
    """
    Dependency que extrai e valida o usuário atual do token JWT
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Extrair token do header Authorization
    token = credentials.credentials
    
    # Decodificar token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    # Extrair user_id do token
    user_id_str: Optional[str] = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception
    
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise credentials_exception
    
    # Buscar usuário no banco
    service = UserService(db)
    try:
        user = await service.get_user_by_id(user_id)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency que garante que o usuário está ativo
    """
    if current_user.status != "ativo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Usuário {current_user.status.value}"
        )
    
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency que garante que o usuário é administrador
    """
    if current_user.type != UserType.ADM:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    
    return current_user
