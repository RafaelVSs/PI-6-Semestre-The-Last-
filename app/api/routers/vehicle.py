from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.db.client import get_db_session
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleResponse, VehicleListResponse
from app.schemas.enums import VehicleType, UserType
from app.services.vehicle_service import VehicleService
from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.common.exceptions.validation_exceptions import ValidationError

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


def check_vehicle_ownership(current_user: User, vehicle_owner_id: UUID) -> bool:
    """Verifica se o usuário atual é dono do veículo ou é admin"""
    is_owner = str(current_user.id) == str(vehicle_owner_id)
    is_admin = current_user.type == UserType.ADM
    return is_owner or is_admin


@router.post("/", response_model=VehicleResponse, status_code=201)
async def create_vehicle(
    vehicle_data: VehicleCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> VehicleResponse:
    """Criar novo veículo"""
    # Validar que usuário só pode criar veículo para si mesmo, exceto admin
    if current_user.type != UserType.ADM and str(vehicle_data.id_usuario) != str(current_user.id):
        raise ValidationError.unauthorized_operation(
            "Usuário só pode criar veículos para si mesmo"
        )
    
    service = VehicleService(db)
    vehicle = await service.create_vehicle(vehicle_data)
    return VehicleResponse.model_validate(vehicle)


@router.get("/", response_model=VehicleListResponse)
async def list_vehicles(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    tipo: Optional[VehicleType] = Query(None, description="Filtrar por tipo de veículo"),
    frota: Optional[str] = Query(None, description="Filtrar por frota"),
    manutencao_vencida: Optional[bool] = Query(None, description="Filtrar por manutenção vencida"),
    search: Optional[str] = Query(None, description="Buscar por placa, modelo ou marca"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> VehicleListResponse:
    """Listar veículos - usuários veem apenas seus veículos, admins veem todos"""
    service = VehicleService(db)
    
    # Usuários não-admin só veem seus próprios veículos
    id_usuario = None if current_user.type == UserType.ADM else current_user.id
    
    vehicles = await service.get_vehicles(
        skip=skip,
        limit=limit,
        id_usuario=id_usuario,
        tipo=tipo,
        frota=frota,
        manutencao_vencida=manutencao_vencida,
        search=search
    )
    
    total = await service.count_vehicles(
        id_usuario=id_usuario,
        tipo=tipo,
        frota=frota,
        manutencao_vencida=manutencao_vencida,
        search=search
    )
    
    return VehicleListResponse(
        vehicles=[VehicleResponse.model_validate(vehicle) for vehicle in vehicles],
        total=total,
        page=(skip // limit) + 1,
        per_page=limit
    )


@router.get("/manutencao-vencida", response_model=list[VehicleResponse])
async def list_vehicles_manutencao_vencida(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> list[VehicleResponse]:
    """Listar veículos com manutenção vencida"""
    service = VehicleService(db)
    
    # Usuários não-admin só veem seus próprios veículos
    id_usuario = None if current_user.type == UserType.ADM else current_user.id
    
    vehicles = await service.get_vehicles_manutencao_vencida(id_usuario)
    return [VehicleResponse.model_validate(vehicle) for vehicle in vehicles]


@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> VehicleResponse:
    """Buscar veículo por ID"""
    service = VehicleService(db)
    vehicle = await service.get_vehicle_by_id(vehicle_id)
    
    # Verificar permissão
    if not check_vehicle_ownership(current_user, vehicle.id_usuario):
        raise ValidationError.unauthorized_operation(
            "Usuário não tem permissão para visualizar este veículo"
        )
    
    return VehicleResponse.model_validate(vehicle)


@router.get("/placa/{placa}", response_model=VehicleResponse)
async def get_vehicle_by_placa(
    placa: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> VehicleResponse:
    """Buscar veículo por placa"""
    service = VehicleService(db)
    vehicle = await service.get_vehicle_by_placa(placa)
    
    # Verificar permissão
    if not check_vehicle_ownership(current_user, vehicle.id_usuario):
        raise ValidationError.unauthorized_operation(
            "Usuário não tem permissão para visualizar este veículo"
        )
    
    return VehicleResponse.model_validate(vehicle)


@router.patch("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: UUID,
    vehicle_data: VehicleUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> VehicleResponse:
    """Atualizar veículo - apenas dono ou admin"""
    service = VehicleService(db)
    vehicle = await service.get_vehicle_by_id(vehicle_id)
    
    # Verificar permissão
    if not check_vehicle_ownership(current_user, vehicle.id_usuario):
        raise ValidationError.unauthorized_operation(
            "Usuário não tem permissão para editar este veículo"
        )
    
    updated_vehicle = await service.update_vehicle(vehicle_id, vehicle_data)
    return VehicleResponse.model_validate(updated_vehicle)


@router.delete("/{vehicle_id}", status_code=204)
async def delete_vehicle(
    vehicle_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Deletar veículo - apenas dono ou admin"""
    service = VehicleService(db)
    vehicle = await service.get_vehicle_by_id(vehicle_id)
    
    # Verificar permissão
    if not check_vehicle_ownership(current_user, vehicle.id_usuario):
        raise ValidationError.unauthorized_operation(
            "Usuário não tem permissão para deletar este veículo"
        )
    
    await service.delete_vehicle(vehicle_id)
    return None


@router.patch("/{vehicle_id}/km", response_model=VehicleResponse)
async def update_vehicle_km(
    vehicle_id: UUID,
    km_atual: int = Query(..., ge=0, description="Quilometragem atual"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> VehicleResponse:
    """Atualizar quilometragem do veículo - apenas dono ou admin"""
    service = VehicleService(db)
    vehicle = await service.get_vehicle_by_id(vehicle_id)
    
    # Verificar permissão
    if not check_vehicle_ownership(current_user, vehicle.id_usuario):
        raise ValidationError.unauthorized_operation(
            "Usuário não tem permissão para atualizar este veículo"
        )
    
    updated_vehicle = await service.update_km(vehicle_id, km_atual)
    return VehicleResponse.model_validate(updated_vehicle)


@router.post("/{vehicle_id}/manutencao", response_model=VehicleResponse)
async def registrar_manutencao(
    vehicle_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> VehicleResponse:
    """Registrar que a manutenção foi realizada - apenas dono ou admin"""
    service = VehicleService(db)
    vehicle = await service.get_vehicle_by_id(vehicle_id)
    
    # Verificar permissão
    if not check_vehicle_ownership(current_user, vehicle.id_usuario):
        raise ValidationError.unauthorized_operation(
            "Usuário não tem permissão para registrar manutenção deste veículo"
        )
    
    updated_vehicle = await service.registrar_manutencao(vehicle_id)
    return VehicleResponse.model_validate(updated_vehicle)
