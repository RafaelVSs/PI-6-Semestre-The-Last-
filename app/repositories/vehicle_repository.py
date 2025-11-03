from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate
from app.schemas.enums import VehicleType
from app.common.exceptions.veiculo_exceptions import VeiculoNotFoundError


class VehicleRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, vehicle_data: VehicleCreate) -> Vehicle:
        """Cria um novo veículo no banco de dados"""
        db_vehicle = Vehicle(
            placa=vehicle_data.placa,
            modelo=vehicle_data.modelo,
            marca=vehicle_data.marca,
            ano=vehicle_data.ano,
            tipo=vehicle_data.tipo,
            id_usuario=vehicle_data.id_usuario,
            frota=vehicle_data.frota,
            km_atual=vehicle_data.km_atual,
            frequencia_km_manutencao=vehicle_data.frequencia_km_manutencao,
            km_prox_manutencao=vehicle_data.km_prox_manutencao,
            capacidade_tanque=vehicle_data.capacidade_tanque,
            km_ultimo_abastecimento=vehicle_data.km_ultimo_abastecimento
        )
        
        self.db.add(db_vehicle)
        await self.db.commit()
        await self.db.refresh(db_vehicle)
        return db_vehicle

    async def get_by_id(self, vehicle_id: UUID) -> Vehicle:
        """Busca um veículo pelo ID"""
        result = await self.db.execute(
            select(Vehicle).where(Vehicle.id == vehicle_id)
        )
        vehicle = result.scalar_one_or_none()
        if not vehicle:
            raise VeiculoNotFoundError.by_id(vehicle_id)
        return vehicle

    async def get_by_placa(self, placa: str) -> Vehicle:
        """Busca um veículo pela placa"""
        result = await self.db.execute(
            select(Vehicle).where(Vehicle.placa == placa)
        )
        vehicle = result.scalar_one_or_none()
        if not vehicle:
            raise VeiculoNotFoundError.by_placa(placa)
        return vehicle

    async def get_all(
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
        query = select(Vehicle)
        
        # Filtro por usuário
        if id_usuario is not None:
            query = query.where(Vehicle.id_usuario == id_usuario)
        
        # Filtro por tipo de veículo
        if tipo is not None:
            query = query.where(Vehicle.tipo == tipo)
        
        # Filtro por frota
        if frota is not None:
            query = query.where(Vehicle.frota == frota)
        
        # Filtro por manutenção vencida
        if manutencao_vencida is not None:
            query = query.where(Vehicle.manutencao_vencida == manutencao_vencida)
            
        # Filtro por busca (placa, modelo, marca)
        if search:
            search_filter = or_(
                Vehicle.placa.ilike(f"%{search}%"),
                Vehicle.modelo.ilike(f"%{search}%"),
                Vehicle.marca.ilike(f"%{search}%")
            )
            query = query.where(search_filter)

        query = query.offset(skip).limit(limit).order_by(Vehicle.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def count(
        self,
        id_usuario: Optional[UUID] = None,
        tipo: Optional[VehicleType] = None,
        frota: Optional[str] = None,
        manutencao_vencida: Optional[bool] = None,
        search: Optional[str] = None
    ) -> int:
        """Conta o número total de veículos com filtros"""
        query = select(func.count(Vehicle.id))

        if id_usuario is not None:
            query = query.where(Vehicle.id_usuario == id_usuario)
        
        if tipo is not None:
            query = query.where(Vehicle.tipo == tipo)
        
        if frota is not None:
            query = query.where(Vehicle.frota == frota)
        
        if manutencao_vencida is not None:
            query = query.where(Vehicle.manutencao_vencida == manutencao_vencida)
        
        if search:
            search_filter = or_(
                Vehicle.placa.ilike(f"%{search}%"),
                Vehicle.modelo.ilike(f"%{search}%"),
                Vehicle.marca.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
        
        result = await self.db.execute(query)
        return result.scalar()

    async def update(self, vehicle_id: UUID, vehicle_data: VehicleUpdate) -> Vehicle:
        """Atualiza um veículo existente"""
        db_vehicle = await self.get_by_id(vehicle_id)

        update_data = vehicle_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_vehicle, field, value)

        await self.db.commit()
        await self.db.refresh(db_vehicle)
        return db_vehicle

    async def delete(self, vehicle_id: UUID) -> bool:
        """Remove permanentemente um veículo do banco"""
        db_vehicle = await self.get_by_id(vehicle_id)

        await self.db.delete(db_vehicle)
        await self.db.commit()
        return True

    async def exists_placa(self, placa: str, exclude_vehicle_id: Optional[UUID] = None) -> bool:
        """Verifica se já existe um veículo com a placa"""
        query = select(Vehicle.id).where(Vehicle.placa == placa)
        
        if exclude_vehicle_id:
            query = query.where(Vehicle.id != exclude_vehicle_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def update_km(self, vehicle_id: UUID, km_atual: int) -> Vehicle:
        """Atualiza a quilometragem atual e verifica manutenção vencida"""
        db_vehicle = await self.get_by_id(vehicle_id)
        
        db_vehicle.km_atual = km_atual
        
        # Verifica se a manutenção está vencida (apenas se km_prox_manutencao estiver definido)
        if db_vehicle.km_prox_manutencao is not None and km_atual >= db_vehicle.km_prox_manutencao:
            db_vehicle.manutencao_vencida = True
        
        await self.db.commit()
        await self.db.refresh(db_vehicle)
        return db_vehicle

    async def registrar_manutencao(self, vehicle_id: UUID) -> Vehicle:
        """Registra que a manutenção foi realizada e calcula próxima"""
        db_vehicle = await self.get_by_id(vehicle_id)
        
        # Calcula próxima manutenção apenas se frequencia_km_manutencao estiver definida
        if db_vehicle.frequencia_km_manutencao is not None:
            db_vehicle.km_prox_manutencao = db_vehicle.km_atual + db_vehicle.frequencia_km_manutencao
        
        db_vehicle.manutencao_vencida = False
        
        await self.db.commit()
        await self.db.refresh(db_vehicle)
        return db_vehicle

    async def get_vehicles_manutencao_vencida(self, id_usuario: Optional[UUID] = None) -> List[Vehicle]:
        """Busca veículos com manutenção vencida"""
        query = select(Vehicle).where(Vehicle.manutencao_vencida == True)
        
        if id_usuario:
            query = query.where(Vehicle.id_usuario == id_usuario)
        
        query = query.order_by(Vehicle.km_atual.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
