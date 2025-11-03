from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.telephone_number import TelephoneNumber
from app.schemas.enums import TelephoneNumberStatus
from app.schemas.telephone_number import TelephoneNumberCreate, TelephoneNumberUpdate
from app.common.exceptions.telephone_number_exceptions import TelephoneNumberNotFoundError


class TelephoneNumberRepository:
    """Repository para acesso a dados de números de telefone"""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, tel_data: TelephoneNumberCreate) -> TelephoneNumber:
        """Cria um novo número de telefone no banco de dados"""
        db_tel = TelephoneNumber(
            id_user=tel_data.id_user,
            number=tel_data.number,
            status=tel_data.status
        )
        
        self.db.add(db_tel)
        await self.db.commit()
        await self.db.refresh(db_tel)
        return db_tel
    
    async def get_by_id(self, tel_id: UUID) -> TelephoneNumber:
        """Busca um número de telefone pelo ID - lança exception se não encontrar"""
        result = await self.db.execute(
            select(TelephoneNumber).where(TelephoneNumber.id == tel_id)
        )
        telephone = result.scalar_one_or_none()
        
        if not telephone:
            raise TelephoneNumberNotFoundError(f"Telefone com ID {tel_id} não encontrado")
        
        return telephone
    
    async def get_by_number(self, number: str) -> TelephoneNumber:
        """Busca um número de telefone pelo número - lança exception se não encontrar"""
        result = await self.db.execute(
            select(TelephoneNumber).where(TelephoneNumber.number == number)
        )
        telephone = result.scalar_one_or_none()
        
        if not telephone:
            raise TelephoneNumberNotFoundError(f"Telefone {number} não encontrado")
        
        return telephone
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[TelephoneNumberStatus] = None,
        user_id: Optional[UUID] = None
    ) -> List[TelephoneNumber]:
        """Busca todos os números de telefone com filtros opcionais"""
        query = select(TelephoneNumber)
        
        if user_id:
            query = query.where(TelephoneNumber.id_user == user_id)
        
        if status:
            query = query.where(TelephoneNumber.status == status)
        
        query = query.offset(skip).limit(limit).order_by(TelephoneNumber.created_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count(
        self,
        status: Optional[TelephoneNumberStatus] = None,
        user_id: Optional[UUID] = None
    ) -> int:
        """Conta números de telefone com filtros opcionais"""
        query = select(func.count(TelephoneNumber.id))
        
        if user_id:
            query = query.where(TelephoneNumber.id_user == user_id)
        
        if status:
            query = query.where(TelephoneNumber.status == status)
        
        result = await self.db.execute(query)
        return result.scalar_one()

    async def update(self, tel_id: UUID, tel_data: TelephoneNumberUpdate) -> TelephoneNumber:
        """Atualiza um número de telefone"""
        tel = await self.get_by_id(tel_id)  # Já lança exception se não encontrar
        
        # Atualiza apenas os campos fornecidos
        update_data = tel_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tel, field, value)
        
        await self.db.commit()
        await self.db.refresh(tel)
        return tel

    async def delete(self, tel_id: UUID) -> None:
        """Remove um número de telefone"""
        tel = await self.get_by_id(tel_id)  # Já lança exception se não encontrar
        
        await self.db.delete(tel)
        await self.db.commit()
