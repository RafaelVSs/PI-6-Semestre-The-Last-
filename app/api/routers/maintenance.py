from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.db.client import get_db_session
from app.schemas.maintenance import MaintenanceCreate, MaintenanceUpdate, MaintenanceResponse, MaintenanceListResponse
from app.schemas.enums import MaintenanceStatus, UserType
from app.services.maintenance_service import MaintenanceService
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.common.exceptions.validation_exceptions import ValidationError

router = APIRouter(prefix="/maintenances", tags=["maintenances"])


@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def create_maintenance(
    maintenance_data: MaintenanceCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Criar nova manutenção e publicar no Pub/Sub"""
    service = MaintenanceService(db)
    result = await service.create_maintenance(maintenance_data)
    
    # Retornar confirmação de envio
    return {
        "message": result["message"],
        "temp_id": result["temp_id"],
        "message_id": result["message_id"],
        "status": result["status"],
        "info": "A manutenção será processada em breve pelo sistema"
    }


@router.get("/", response_model=MaintenanceListResponse, status_code=status.HTTP_200_OK)
async def list_maintenances(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    placa: Optional[str] = Query(None, description="Filtrar por placa"),
    status_param: Optional[MaintenanceStatus] = Query(None, alias="status", description="Filtrar por status"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> MaintenanceListResponse:
    """Listar manutenções"""
    service = MaintenanceService(db)
    
    maintenances = await service.get_maintenances(
        skip=skip,
        limit=limit,
        placa=placa,
        status=status_param
    )
    
    total = await service.count_maintenances(
        placa=placa,
        status=status_param
    )
    
    return MaintenanceListResponse(
        maintenances=[MaintenanceResponse.model_validate(m) for m in maintenances],
        total=total,
        page=(skip // limit) + 1,
        per_page=limit
    )


@router.get("/placa/{placa}", response_model=list[MaintenanceResponse], status_code=status.HTTP_200_OK)
async def get_maintenances_by_placa(
    placa: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> list[MaintenanceResponse]:
    """Buscar manutenções por placa"""
    service = MaintenanceService(db)
    maintenances = await service.get_maintenances_by_placa(placa)
    return [MaintenanceResponse.model_validate(m) for m in maintenances]


@router.get("/status/{status_value}", response_model=list[MaintenanceResponse], status_code=status.HTTP_200_OK)
async def get_maintenances_by_status(
    status_value: MaintenanceStatus,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> list[MaintenanceResponse]:
    """Buscar manutenções por status"""
    service = MaintenanceService(db)
    maintenances = await service.get_maintenances_by_status(status_value)
    return [MaintenanceResponse.model_validate(m) for m in maintenances]


@router.get("/{maintenance_id}", response_model=MaintenanceResponse, status_code=status.HTTP_200_OK)
async def get_maintenance(
    maintenance_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> MaintenanceResponse:
    """Buscar manutenção por ID"""
    service = MaintenanceService(db)
    maintenance = await service.get_maintenance_by_id(maintenance_id)
    return MaintenanceResponse.model_validate(maintenance)


@router.patch("/{maintenance_id}", response_model=MaintenanceResponse, status_code=status.HTTP_200_OK)
async def update_maintenance(
    maintenance_id: UUID,
    maintenance_data: MaintenanceUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> MaintenanceResponse:
    """Atualizar manutenção"""
    service = MaintenanceService(db)
    maintenance = await service.update_maintenance(maintenance_id, maintenance_data)
    return MaintenanceResponse.model_validate(maintenance)


@router.delete("/{maintenance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_maintenance(
    maintenance_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Deletar manutenção - restrito a administradores"""
    if current_user.type != UserType.ADM:
        raise ValidationError.unauthorized_operation(
            "Apenas administradores podem deletar manutenções"
        )
    
    service = MaintenanceService(db)
    await service.delete_maintenance(maintenance_id)
    return None


@router.post("/{maintenance_id}/concluir", response_model=MaintenanceResponse, status_code=status.HTTP_200_OK)
async def concluir_manutencao(
    maintenance_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> MaintenanceResponse:
    """Marcar manutenção como concluída"""
    service = MaintenanceService(db)
    maintenance = await service.concluir_manutencao(maintenance_id)
    return MaintenanceResponse.model_validate(maintenance)


@router.post("/{maintenance_id}/cancelar", response_model=MaintenanceResponse, status_code=status.HTTP_200_OK)
async def cancelar_manutencao(
    maintenance_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> MaintenanceResponse:
    """Marcar manutenção como cancelada"""
    service = MaintenanceService(db)
    maintenance = await service.cancelar_manutencao(maintenance_id)
    return MaintenanceResponse.model_validate(maintenance)
