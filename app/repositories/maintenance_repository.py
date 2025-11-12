from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.maintenance import Maintenance
from app.schemas.maintenance import MaintenanceCreate, MaintenanceUpdate
from app.schemas.enums import MaintenanceStatus
from app.common.exceptions.manutencao_exceptions import ManutencaoNotFoundError


class MaintenanceRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, maintenance_data: MaintenanceCreate) -> Maintenance:
        """Cria uma nova manutenção no banco de dados"""
        db_maintenance = Maintenance(
            placa=maintenance_data.placa,
            km_atual=maintenance_data.km_atual,
            oleo=maintenance_data.oleo,
            filtro_oleo=maintenance_data.filtro_oleo,
            filtro_combustivel=maintenance_data.filtro_combustivel,
            filtro_ar=maintenance_data.filtro_ar,
            engraxamento=maintenance_data.engraxamento,
            status=maintenance_data.status
        )
        
        self.db.add(db_maintenance)
        await self.db.commit()
        await self.db.refresh(db_maintenance)
        return db_maintenance

    async def get_by_id(self, maintenance_id: UUID) -> Maintenance:
        """Busca uma manutenção pelo ID"""
        result = await self.db.execute(
            select(Maintenance).where(Maintenance.id == maintenance_id)
        )
        maintenance = result.scalar_one_or_none()
        if not maintenance:
            raise ManutencaoNotFoundError.by_id(maintenance_id)
        return maintenance

    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        placa: Optional[str] = None,
        status: Optional[MaintenanceStatus] = None
    ) -> List[Maintenance]:
        """Lista manutenções com filtros e paginação"""
        query = select(Maintenance)
        
        # Filtro por placa
        if placa:
            query = query.where(Maintenance.placa == placa)
        
        # Filtro por status
        if status is not None:
            query = query.where(Maintenance.status == status)

        query = query.offset(skip).limit(limit).order_by(Maintenance.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def count(
        self,
        placa: Optional[str] = None,
        status: Optional[MaintenanceStatus] = None
    ) -> int:
        """Conta o número total de manutenções com filtros"""
        query = select(func.count(Maintenance.id))

        if placa:
            query = query.where(Maintenance.placa == placa)
        
        if status is not None:
            query = query.where(Maintenance.status == status)
        
        result = await self.db.execute(query)
        return result.scalar()

    async def update(self, maintenance_id: UUID, maintenance_data: MaintenanceUpdate) -> Maintenance:
        """Atualiza uma manutenção existente"""
        db_maintenance = await self.get_by_id(maintenance_id)

        update_data = maintenance_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_maintenance, field, value)

        await self.db.commit()
        await self.db.refresh(db_maintenance)
        return db_maintenance

    async def delete(self, maintenance_id: UUID) -> bool:
        """Remove permanentemente uma manutenção do banco"""
        db_maintenance = await self.get_by_id(maintenance_id)

        await self.db.delete(db_maintenance)
        await self.db.commit()
        return True

    async def update_status(self, maintenance_id: UUID, status: MaintenanceStatus) -> Maintenance:
        """Atualiza o status de uma manutenção"""
        db_maintenance = await self.get_by_id(maintenance_id)
        db_maintenance.status = status
        
        await self.db.commit()
        await self.db.refresh(db_maintenance)
        return db_maintenance

    async def get_by_placa(self, placa: str) -> List[Maintenance]:
        """Busca manutenções por placa"""
        result = await self.db.execute(
            select(Maintenance)
            .where(Maintenance.placa == placa)
            .order_by(Maintenance.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_by_status(self, status: MaintenanceStatus) -> List[Maintenance]:
        """Busca manutenções por status"""
        result = await self.db.execute(
            select(Maintenance)
            .where(Maintenance.status == status)
            .order_by(Maintenance.created_at.desc())
        )
        return result.scalars().all()
