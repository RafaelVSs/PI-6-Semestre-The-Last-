from typing import Optional, List
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.telephone_number_repository import TelephoneNumberRepository
from app.models.telephone_number import TelephoneNumber
from app.schemas.telephone_number import TelephoneNumberCreate, TelephoneNumberUpdate
from app.schemas.enums import TelephoneNumberStatus
from app.common.exceptions.telephone_number_exceptions import (
    TelephoneNumberAlreadyExistsError,
    TelephoneNumberNotFoundError
)
from app.common.exceptions.validation_exceptions import ValidationError


class TelephoneNumberService:
    """Service para lógica de negócio de números de telefone"""
    
    def __init__(self, db: AsyncSession):
        self.repository = TelephoneNumberRepository(db)
    
    async def create_telephone(self, telephone_data: TelephoneNumberCreate) -> TelephoneNumber:
        """Criar novo número de telefone"""
        # Validar formato do número (você pode adicionar mais validações)
        if not telephone_data.number.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValidationError("Número de telefone deve conter apenas dígitos, +, - ou espaços")
        
        try:
            return await self.repository.create(telephone_data)
        except IntegrityError as e:
            # Verificar se é violação de unique constraint no número
            if 'uq_telephone_number' in str(e) or 'unique constraint' in str(e).lower():
                raise TelephoneNumberAlreadyExistsError(f"Número {telephone_data.number} já está cadastrado")
            # Se for outro tipo de IntegrityError, re-raise
            raise
    
    async def get_telephone_by_id(self, telephone_id: UUID) -> TelephoneNumber:
        """Buscar telefone por ID"""
        return await self.repository.get_by_id(telephone_id)
    
    async def get_telephones(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[TelephoneNumberStatus] = None,
        user_id: Optional[UUID] = None
    ) -> List[TelephoneNumber]:
        """Listar telefones com filtros"""
        return await self.repository.get_all(
            skip=skip,
            limit=limit,
            status=status,
            user_id=user_id
        )
    
    async def count_telephones(
        self,
        status: Optional[TelephoneNumberStatus] = None,
        user_id: Optional[UUID] = None
    ) -> int:
        """Contar telefones com filtros"""
        return await self.repository.count(
            status=status,
            user_id=user_id
        )
    
    async def update_telephone(
        self,
        telephone_id: UUID,
        telephone_data: TelephoneNumberUpdate
    ) -> TelephoneNumber:
        """Atualizar telefone"""
        # Validar número se fornecido
        if telephone_data.number:
            if not telephone_data.number.replace('+', '').replace('-', '').replace(' ', '').isdigit():
                raise ValidationError("Número de telefone deve conter apenas dígitos, +, - ou espaços")
        
        try:
            return await self.repository.update(telephone_id, telephone_data)
        except IntegrityError:
            raise TelephoneNumberAlreadyExistsError(f"Número {telephone_data.number} já está cadastrado")
    
    async def delete_telephone(self, telephone_id: UUID) -> None:
        """Deletar telefone"""
        await self.repository.delete(telephone_id)
