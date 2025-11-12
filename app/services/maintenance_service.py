from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.maintenance_repository import MaintenanceRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.models.maintenance import Maintenance
from app.schemas.maintenance import MaintenanceCreate, MaintenanceUpdate
from app.schemas.enums import MaintenanceStatus
from app.common.exceptions.validation_exceptions import ValidationError
from app.common.exceptions.veiculo_exceptions import VeiculoNotFoundError


class MaintenanceService:
    def __init__(self, db: AsyncSession):
        self.repo = MaintenanceRepository(db)
        self.vehicle_repo = VehicleRepository(db)
    
    async def create_maintenance(self, maintenance_data: MaintenanceCreate) -> Maintenance:
        """Cria uma nova manutenção com validações de negócio"""
        # Validar se o veículo existe
        try:
            vehicle = await self.vehicle_repo.get_by_placa(maintenance_data.placa)
        except:
            raise VeiculoNotFoundError.by_placa(maintenance_data.placa)
        
        # Validar KM atual
        if maintenance_data.km_atual < 0:
            raise ValidationError.invalid_field("km_atual", "Quilometragem não pode ser negativa")
        
        # Validar que pelo menos um item de manutenção foi selecionado
        items = [
            maintenance_data.oleo,
            maintenance_data.filtro_oleo,
            maintenance_data.filtro_combustivel,
            maintenance_data.filtro_ar,
            maintenance_data.engraxamento
        ]
        if not any(items):
            raise ValidationError.invalid_field(
                "manutencoes",
                "Pelo menos um item de manutenção deve ser selecionado"
            )
        
        return await self.repo.create(maintenance_data)

    async def get_maintenance_by_id(self, maintenance_id: UUID) -> Maintenance:
        """Busca uma manutenção pelo ID"""
        return await self.repo.get_by_id(maintenance_id)

    async def get_maintenances(
        self,
        skip: int = 0, 
        limit: int = 100,
        placa: Optional[str] = None,
        status: Optional[MaintenanceStatus] = None
    ) -> List[Maintenance]:
        """Lista manutenções com filtros e paginação"""
        return await self.repo.get_all(
            skip=skip,
            limit=limit,
            placa=placa,
            status=status
        )

    async def count_maintenances(
        self,
        placa: Optional[str] = None,
        status: Optional[MaintenanceStatus] = None
    ) -> int:
        """Conta o número total de manutenções"""
        return await self.repo.count(
            placa=placa,
            status=status
        )

    async def update_maintenance(
        self, 
        maintenance_id: UUID, 
        maintenance_data: MaintenanceUpdate
    ) -> Maintenance:
        """Atualiza uma manutenção existente com validações"""
        # Validar KM se fornecido
        if maintenance_data.km_atual is not None and maintenance_data.km_atual < 0:
            raise ValidationError.invalid_field("km_atual", "Quilometragem não pode ser negativa")
        
        return await self.repo.update(maintenance_id, maintenance_data)

    async def delete_maintenance(self, maintenance_id: UUID) -> bool:
        """Remove uma manutenção"""
        return await self.repo.delete(maintenance_id)

    async def update_status(
        self, 
        maintenance_id: UUID, 
        status: MaintenanceStatus
    ) -> Maintenance:
        """Atualiza o status de uma manutenção"""
        return await self.repo.update_status(maintenance_id, status)

    async def get_maintenances_by_placa(self, placa: str) -> List[Maintenance]:
        """Busca manutenções por placa"""
        # Validar se veículo existe
        try:
            await self.vehicle_repo.get_by_placa(placa)
        except:
            raise VeiculoNotFoundError.by_placa(placa)
        
        return await self.repo.get_by_placa(placa)

    async def get_maintenances_by_status(self, status: MaintenanceStatus) -> List[Maintenance]:
        """Busca manutenções por status"""
        return await self.repo.get_by_status(status)
    
    async def concluir_manutencao(self, maintenance_id: UUID) -> Maintenance:
        """Marca manutenção como concluída"""
        return await self.update_status(maintenance_id, MaintenanceStatus.CONCLUIDA)
    
    async def cancelar_manutencao(self, maintenance_id: UUID) -> Maintenance:
        """Marca manutenção como cancelada"""
        return await self.update_status(maintenance_id, MaintenanceStatus.CANCELADA)
