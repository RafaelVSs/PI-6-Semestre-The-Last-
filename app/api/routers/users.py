from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.db.client import get_db_session
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.schemas.enums import UserStatus, UserType
from app.services.user_service import UserService
from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db_session)
) -> UserResponse:
    """Criar novo usuário - endpoint público para registro"""
    service = UserService(db)
    user = await service.create_user(user_data)
    return UserResponse.model_validate(user)


@router.get("/", response_model=UserListResponse, status_code=status.HTTP_200_OK)
async def list_users(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    status_param: Optional[UserStatus] = Query(None, alias="status", description="Filtrar por status"),
    user_type: Optional[UserType] = Query(None, description="Filtrar por tipo de usuário"),
    search: Optional[str] = Query(None, description="Buscar por nome ou email"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_admin_user)
) -> UserListResponse:
    """Listar usuários - restrito a administradores"""
    service = UserService(db)
    users = await service.get_users(
        skip=skip, 
        limit=limit, 
        status=status_param,
        user_type=user_type,
        search=search
    )
    total = await service.count_users(
        status=status_param,
        user_type=user_type,
        search=search
    )
    
    return UserListResponse(
        users=[UserResponse.model_validate(user) for user in users],
        total=total,
        page=(skip // limit) + 1,
        per_page=limit
    )


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> UserResponse:
    """Buscar usuário por ID"""
    service = UserService(db)
    user = await service.get_user_by_id(user_id)
    return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_admin_user) 
) -> UserResponse:
    """Atualizar usuário - restrito a administradores"""
    service = UserService(db)
    user = await service.update_user(user_id, user_data)
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    hard_delete: bool = Query(False, description="Exclusão permanente"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_admin_user)
):
    """Deletar usuário - restrito a administradores"""
    service = UserService(db)
    
    if hard_delete:
        await service.hard_delete_user(user_id)
    else:
        await service.delete_user(user_id)
    
    return None


@router.post("/{user_id}/activate", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def activate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_admin_user)
) -> UserResponse:
    """Ativar usuário - restrito a administradores"""
    service = UserService(db)
    user = await service.activate_user(user_id)
    return UserResponse.model_validate(user)


@router.post("/{user_id}/deactivate", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def deactivate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_admin_user)
) -> UserResponse:
    """Desativar usuário - restrito a administradores"""
    service = UserService(db)
    user = await service.deactivate_user(user_id)
    return UserResponse.model_validate(user)


@router.get("/email/{email}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_by_email(
    email: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> UserResponse:
    """Buscar usuário por email"""
    service = UserService(db)
    user = await service.get_user_by_email(email)
    return UserResponse.model_validate(user)


@router.get("/cpf/{cpf}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_by_cpf(
    cpf: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> UserResponse:
    """Buscar usuário por CPF"""
    service = UserService(db)
    user = await service.get_user_by_cpf(cpf)
    return UserResponse.model_validate(user)


@router.get("/type/{user_type}", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
async def get_users_by_type(
    user_type: UserType,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> list[UserResponse]:
    """Buscar usuários por tipo"""
    service = UserService(db)
    users = await service.get_users_by_type(user_type)
    return [UserResponse.model_validate(user) for user in users]