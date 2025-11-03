from typing import Optional, List
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.vehicle_repository import VehicleRepository
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate
from app.schemas.enums import VehicleType
from app.common.exceptions.veiculo_exceptions import VeiculoAlreadyExistsError
from app.common.exceptions.validation_exceptions import ValidationError


class VehicleService:
    def __init__(self, db: AsyncSession):
        self.repo = VehicleRepository(db)
    
    async def create_vehicle(self, vehicle_data: VehicleCreate) -> Vehicle:
        """Cria um novo veículo com validações de negócio"""
        try:
            # Validar placa única
            if await self.repo.exists_placa(vehicle_data.placa):
                raise VeiculoAlreadyExistsError.by_placa(vehicle_data.placa)
            
            # Validações de negócio
            if vehicle_data.km_atual < 0:
                raise ValidationError.invalid_field("km_atual", "Quilometragem não pode ser negativa")
            
            # Validar km_prox_manutencao apenas se fornecido
            if vehicle_data.km_prox_manutencao is not None and vehicle_data.km_prox_manutencao < vehicle_data.km_atual:
                raise ValidationError.invalid_field(
                    "km_prox_manutencao", 
                    "KM da próxima manutenção deve ser maior que KM atual"
                )
            
            if vehicle_data.capacidade_tanque <= 0:
                raise ValidationError.invalid_field(
                    "capacidade_tanque",
                    "Capacidade do tanque deve ser maior que zero"
                )
            
            # Validar frequencia_km_manutencao apenas se fornecido
            if vehicle_data.frequencia_km_manutencao is not None and vehicle_data.frequencia_km_manutencao <= 0:
                raise ValidationError.invalid_field(
                    "frequencia_km_manutencao",
                    "Frequência de manutenção deve ser maior que zero"
                )
            
            return await self.repo.create(vehicle_data)
            
        except IntegrityError as e:
            # Fallback para erros de constraint do banco
            if "placa" in str(e.orig).lower():
                raise VeiculoAlreadyExistsError.by_placa(vehicle_data.placa)
            else:
                raise

    async def get_vehicle_by_id(self, vehicle_id: UUID) -> Vehicle:
        """Busca um veículo pelo ID"""
        return await self.repo.get_by_id(vehicle_id)

    async def get_vehicle_by_placa(self, placa: str) -> Vehicle:
        """Busca um veículo pela placa"""
        return await self.repo.get_by_placa(placa)

    async def get_vehicles(
        self,
        skip: int = 0, 
        limit: int = 100,
        id_usuario: Optional[UUID] = None,
        tipo: Optional[VehicleType] = None,
        frota: Optional[str] = None,
        manutencao_vencida: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[Vehicle]:
        """Lista veículos com filtros e paginação"""
        return await self.repo.get_all(
            skip=skip,
            limit=limit,
            id_usuario=id_usuario,
            tipo=tipo,
            frota=frota,
            manutencao_vencida=manutencao_vencida,
            search=search
        )

    async def count_vehicles(
        self,
        id_usuario: Optional[UUID] = None,
        tipo: Optional[VehicleType] = None,
        frota: Optional[str] = None,
        manutencao_vencida: Optional[bool] = None,
        search: Optional[str] = None
    ) -> int:
        """Conta o número total de veículos"""
        return await self.repo.count(
            id_usuario=id_usuario,
            tipo=tipo,
            frota=frota,
            manutencao_vencida=manutencao_vencida,
            search=search
        )

    async def update_vehicle(self, vehicle_id: UUID, vehicle_data: VehicleUpdate) -> Vehicle:
        """Atualiza um veículo existente com validações"""
        # Validar placa única se estiver sendo alterada
        if vehicle_data.placa and await self.repo.exists_placa(
            vehicle_data.placa, 
            exclude_vehicle_id=vehicle_id
        ):
            raise VeiculoAlreadyExistsError.by_placa(vehicle_data.placa)
        
        # Validações de campos numéricos
        if vehicle_data.km_atual is not None and vehicle_data.km_atual < 0:
            raise ValidationError.invalid_field("km_atual", "Quilometragem não pode ser negativa")
        
        if vehicle_data.capacidade_tanque is not None and vehicle_data.capacidade_tanque <= 0:
            raise ValidationError.invalid_field(
                "capacidade_tanque",
                "Capacidade do tanque deve ser maior que zero"
            )
        
        if vehicle_data.frequencia_km_manutencao is not None and vehicle_data.frequencia_km_manutencao <= 0:
            raise ValidationError.invalid_field(
                "frequencia_km_manutencao",
                "Frequência de manutenção deve ser maior que zero"
            )
        
        return await self.repo.update(vehicle_id, vehicle_data)

    async def delete_vehicle(self, vehicle_id: UUID) -> bool:
        """Remove um veículo"""
        return await self.repo.delete(vehicle_id)

    async def update_km(self, vehicle_id: UUID, km_atual: int) -> Vehicle:
        """Atualiza a quilometragem do veículo"""
        if km_atual < 0:
            raise ValidationError.invalid_field("km_atual", "Quilometragem não pode ser negativa")
        
        return await self.repo.update_km(vehicle_id, km_atual)

    async def registrar_manutencao(self, vehicle_id: UUID) -> Vehicle:
        """Registra que a manutenção foi realizada"""
        return await self.repo.registrar_manutencao(vehicle_id)

    async def get_vehicles_manutencao_vencida(
        self, 
        id_usuario: Optional[UUID] = None
    ) -> List[Vehicle]:
        """Busca veículos com manutenção vencida"""
        return await self.repo.get_vehicles_manutencao_vencida(id_usuario)
