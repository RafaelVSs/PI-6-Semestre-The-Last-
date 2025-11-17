from typing import Optional
from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.db.client import get_db_session
from app.schemas.refuel import (
    RefuelCreate,
    RefuelResponse,
    RefuelListResponse,
    RefuelUpdate,
    RefuelPublishResponse
)
from app.schemas.enums import UserType
from app.services.refuel_service import RefuelService
from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.models.user import User

router = APIRouter(prefix="/refuels", tags=["refuels"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_refuel(
    refuel_data: RefuelCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Criar abastecimento 
    """
    service = RefuelService(db)
    refuel_data.id_usuario = current_user.id
    
    refuel = await service.create_refuel(refuel_data)
    return RefuelResponse.model_validate(refuel)
    


@router.get("/", response_model=RefuelListResponse, status_code=status.HTTP_200_OK)
async def list_refuels(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    placa: Optional[str] = Query(None, description="Filtrar por placa"),
    id_usuario: Optional[UUID] = Query(None, description="Filtrar por ID do usuário"),
    data_inicio: Optional[date] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[date] = Query(None, description="Data fim (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> RefuelListResponse:
    """
    Listar abastecimentos do banco de dados.
    Usuários comuns veem apenas seus próprios.
    Admins veem todos.
    """
    service = RefuelService(db)
    
    # Se não for admin, forçar filtro pelo próprio id_usuario
    if current_user.type != UserType.ADM:
        id_usuario = current_user.id
    
    refuels = await service.get_refuels(
        skip=skip,
        limit=limit,
        placa=placa,
        id_usuario=id_usuario,
        data_inicio=data_inicio,
        data_fim=data_fim
    )
    
    total = await service.count_refuels(
        placa=placa,
        id_usuario=id_usuario,
        data_inicio=data_inicio,
        data_fim=data_fim
    )
    
    return RefuelListResponse(
        refuels=[RefuelResponse.model_validate(r) for r in refuels],
        total=total,
        page=(skip // limit) + 1,
        per_page=limit
    )


@router.get("/{refuel_id}", response_model=RefuelResponse, status_code=status.HTTP_200_OK)
async def get_refuel(
    refuel_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> RefuelResponse:
    """Buscar abastecimento por ID - apenas dono ou admin"""
    service = RefuelService(db)
    refuel = await service.get_refuel_by_id(refuel_id)
    
    # Validar permissão: apenas o dono ou admin pode ver
    if current_user.type != UserType.ADM and refuel.id_usuario != current_user.id:
        from app.common.exceptions.validation_exceptions import ValidationError
        raise ValidationError.unauthorized_operation(
            "Você não tem permissão para acessar este recurso"
        )
    
    return RefuelResponse.model_validate(refuel)


@router.patch("/{refuel_id}", response_model=RefuelResponse, status_code=status.HTTP_200_OK)
async def update_refuel(
    refuel_id: UUID,
    refuel_data: RefuelUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_admin_user)
) -> RefuelResponse:
    """Atualizar abastecimento - apenas admin"""
    service = RefuelService(db)
    refuel = await service.update_refuel(refuel_id, refuel_data)
    return RefuelResponse.model_validate(refuel)


@router.delete("/{refuel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_refuel(
    refuel_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_admin_user)
):
    """Deletar abastecimento - apenas admin"""
    service = RefuelService(db)
    await service.delete_refuel(refuel_id)
    return None
