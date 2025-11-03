from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.db.client import get_db_session
from app.schemas.telephone_number import (
    TelephoneNumberCreate,
    TelephoneNumberUpdate,
    TelephoneNumberResponse,
    TelephoneNumberListResponse
)
from app.schemas.enums import TelephoneNumberStatus, UserType
from app.services.telephone_number_service import TelephoneNumberService
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.common.exceptions.validation_exceptions import ValidationError

router = APIRouter(prefix="/telephones", tags=["telephones"])


def check_telephone_ownership(telephone_id_user: UUID, current_user: User):
    """
    Valida se o usuário atual é o dono do telefone ou um admin.
    Lança ValidationError se não for.
    """
    is_owner = telephone_id_user == current_user.id
    is_admin = current_user.type == UserType.ADM
    
    if not (is_owner or is_admin):
        raise ValidationError.unauthorized_operation(
            "Você não tem permissão para acessar este recurso"
        )


@router.post("/", response_model=TelephoneNumberResponse, status_code=status.HTTP_201_CREATED)
async def create_telephone(
    telephone_data: TelephoneNumberCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> TelephoneNumberResponse:
    """
    Criar número de telefone.
    Usuário pode criar para si mesmo ou admin pode criar para qualquer usuário.
    """
    # Validar que usuário comum só pode criar telefone para si mesmo
    if current_user.type != UserType.ADM and telephone_data.id_user != current_user.id:
        raise ValidationError.unauthorized_operation(
            "Você só pode criar telefones para si mesmo"
        )
    
    service = TelephoneNumberService(db)
    telephone = await service.create_telephone(telephone_data)
    return TelephoneNumberResponse.model_validate(telephone)


@router.get("/", response_model=TelephoneNumberListResponse, status_code=status.HTTP_200_OK)
async def list_telephones(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    status_filter: Optional[TelephoneNumberStatus] = Query(None, description="Filtrar por status"),
    user_id: Optional[UUID] = Query(None, description="Filtrar por ID do usuário"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> TelephoneNumberListResponse:
    """
    Listar telefones.
    Usuário comum vê apenas seus próprios telefones.
    Admin vê todos (ou filtra por user_id).
    """
    service = TelephoneNumberService(db)
    
    # Se não for admin, forçar filtro pelo próprio user_id
    if current_user.type != UserType.ADM:
        user_id = current_user.id
    
    telephones = await service.get_telephones(
        skip=skip,
        limit=limit,
        status=status_filter,
        user_id=user_id
    )
    
    total = await service.count_telephones(
        status=status_filter,
        user_id=user_id
    )
    
    return TelephoneNumberListResponse(
        telephone_numbers=[TelephoneNumberResponse.model_validate(t) for t in telephones],
        total=total,
        page=(skip // limit) + 1,
        per_page=limit
    )


@router.get("/{telephone_id}", response_model=TelephoneNumberResponse, status_code=status.HTTP_200_OK)
async def get_telephone(
    telephone_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> TelephoneNumberResponse:
    """Buscar telefone por ID - apenas dono ou admin"""
    service = TelephoneNumberService(db)
    telephone = await service.get_telephone_by_id(telephone_id)
    
    # Validar permissão
    check_telephone_ownership(telephone.id_user, current_user)
    
    return TelephoneNumberResponse.model_validate(telephone)


@router.patch("/{telephone_id}", response_model=TelephoneNumberResponse, status_code=status.HTTP_200_OK)
async def update_telephone(
    telephone_id: UUID,
    telephone_data: TelephoneNumberUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> TelephoneNumberResponse:
    """Atualizar telefone - apenas dono ou admin"""
    service = TelephoneNumberService(db)
    
    # Buscar telefone para validar propriedade
    telephone = await service.get_telephone_by_id(telephone_id)
    
    # Validar permissão
    check_telephone_ownership(telephone.id_user, current_user)
    
    # Atualizar
    updated_telephone = await service.update_telephone(telephone_id, telephone_data)
    return TelephoneNumberResponse.model_validate(updated_telephone)


@router.delete("/{telephone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_telephone(
    telephone_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Deletar telefone - apenas dono ou admin"""
    service = TelephoneNumberService(db)
    
    # Buscar telefone para validar propriedade
    telephone = await service.get_telephone_by_id(telephone_id)
    
    # Validar permissão
    check_telephone_ownership(telephone.id_user, current_user)
    
    # Deletar
    await service.delete_telephone(telephone_id)
    return None