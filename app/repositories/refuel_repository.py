from typing import Optional, List
from datetime import date

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refuel import Refuel
from app.schemas.refuel import RefuelCreate, RefuelUpdate
from app.common.exceptions.abastecimento_exceptions import AbastecimentoNotFoundError


class RefuelRepository:
    """Repository para acesso a dados de abastecimento"""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, refuel_data: RefuelCreate) -> Refuel:
        """Cria um novo abastecimento no banco de dados"""
        db_refuel = Refuel(
            data=refuel_data.data,
            hora=refuel_data.hora,
            km=refuel_data.km,
            litros=refuel_data.litros,
            tipo_combustivel=refuel_data.tipo_combustivel,
            valor_litro=refuel_data.valor_litro,
            posto=refuel_data.posto,
            tanque_cheio=refuel_data.tanque_cheio,
            media=refuel_data.media,
            id_usuario=refuel_data.id_usuario,
            placa=refuel_data.placa
        )
        
        self.db.add(db_refuel)
        await self.db.commit()
        await self.db.refresh(db_refuel)
        return db_refuel
    
    async def get_by_id(self, refuel_id: int) -> Refuel:
        """Busca um abastecimento pelo ID - lança exception se não encontrar"""
        result = await self.db.execute(
            select(Refuel).where(Refuel.id == refuel_id)
        )
        refuel = result.scalar_one_or_none()
        
        if not refuel:
            raise AbastecimentoNotFoundError.by_id(refuel_id)
        
        return refuel
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        placa: Optional[str] = None,
        id_usuario: Optional[str] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None
    ) -> List[Refuel]:
        """Busca todos os abastecimentos com filtros opcionais"""
        query = select(Refuel)
        
        if placa:
            query = query.where(Refuel.placa == placa)
        
        if id_usuario:
            query = query.where(Refuel.id_usuario == id_usuario)
        
        if data_inicio:
            query = query.where(Refuel.data >= data_inicio)
        
        if data_fim:
            query = query.where(Refuel.data <= data_fim)
        
        query = query.offset(skip).limit(limit).order_by(Refuel.data.desc(), Refuel.hora.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count(
        self,
        placa: Optional[str] = None,
        id_usuario: Optional[str] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None
    ) -> int:
        """Conta abastecimentos com filtros opcionais"""
        query = select(func.count(Refuel.id))
        
        if placa:
            query = query.where(Refuel.placa == placa)
        
        if id_usuario:
            query = query.where(Refuel.id_usuario == id_usuario)
        
        if data_inicio:
            query = query.where(Refuel.data >= data_inicio)
        
        if data_fim:
            query = query.where(Refuel.data <= data_fim)
        
        result = await self.db.execute(query)
        return result.scalar_one()

    async def update(self, refuel_id: int, refuel_data: RefuelUpdate) -> Refuel:
        """Atualiza um abastecimento"""
        refuel = await self.get_by_id(refuel_id)  # Já lança exception se não encontrar
        
        # Atualiza apenas os campos fornecidos
        update_data = refuel_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(refuel, field, value)
        
        await self.db.commit()
        await self.db.refresh(refuel)
        return refuel

    async def delete(self, refuel_id: int) -> None:
        """Remove um abastecimento"""
        refuel = await self.get_by_id(refuel_id)  # Já lança exception se não encontrar
        
        await self.db.delete(refuel)
        await self.db.commit()
