from typing import Optional, List
from uuid import UUID as UuidType

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.enums import UserStatus, UserType
from app.common.exceptions import UserAlreadyExistsError, ValidationError
from app.core.security import hash_password, validate_password_strength


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Cria um novo usuário com validações de negócio"""
        try:
            if await self.repo.exists_email(user_data.email):
                raise UserAlreadyExistsError.by_email(user_data.email)

            if await self.repo.exists_cpf(user_data.cpf):
                raise UserAlreadyExistsError.by_cpf(user_data.cpf)
            
            # Validar força da senha
            is_valid, errors = validate_password_strength(user_data.password)
            if not is_valid:
                raise ValidationError.password_strength(errors)
            
            # Hash da senha antes de salvar
            user_data.password = hash_password(user_data.password)
            
            return await self.repo.create(user_data)
            
        except IntegrityError as e:
            # Fallback para erros de constraint do banco
            if "uq_user_email" in str(e.orig):
                raise UserAlreadyExistsError.by_email(user_data.email)
            elif "uq_user_cpf" in str(e.orig):
                raise UserAlreadyExistsError.by_cpf(user_data.cpf)
            else:
                raise  # Re-lança erro não tratado

    async def get_user_by_id(self, user_id: UuidType) -> User:
        """Busca um usuário pelo ID"""
        return await self.repo.get_by_id(user_id)

    async def get_user_by_email(self, email: str) -> User:
        """Busca um usuário pelo email"""
        return await self.repo.get_by_email(email)

    async def get_user_by_cpf(self, cpf: str) -> User:
        """Busca um usuário pelo CPF"""
        return await self.repo.get_by_cpf(cpf)

    async def get_users(
        self,
        skip: int = 0, 
        limit: int = 100,
        status: Optional[UserStatus] = None,
        user_type: Optional[UserType] = None,
        search: Optional[str] = None
    ) -> List[User]:
        """Lista usuários com filtros e paginação"""
        return await self.repo.get_all(
            skip=skip,
            limit=limit,
            status=status,
            user_type=user_type,
            search=search
        )

    async def count_users(
        self,
        status: Optional[UserStatus] = None,
        user_type: Optional[UserType] = None,
        search: Optional[str] = None
    ) -> int:
        """Conta o número total de usuários"""
        return await self.repo.count(
            status=status,
            user_type=user_type,
            search=search
        )

    async def update_user(self, user_id: UuidType, user_data: UserUpdate) -> User:
        """Atualiza um usuário existente com validações"""
        # Validar email único
        if user_data.email and await self.repo.exists_email(user_data.email, exclude_user_id=user_id):
            raise UserAlreadyExistsError.by_email(user_data.email)
        
        # Validar CPF único
        if user_data.cpf and await self.repo.exists_cpf(user_data.cpf, exclude_user_id=user_id):
            raise UserAlreadyExistsError.by_cpf(user_data.cpf)

        # Validar e hash de senha se fornecida
        if user_data.password:
            is_valid, errors = validate_password_strength(user_data.password)
            if not is_valid:
                raise ValidationError.password_strength(errors)
            user_data.password = hash_password(user_data.password)
        
        return await self.repo.update(user_id, user_data)

    async def delete_user(self, user_id: UuidType) -> bool:
        """Remove um usuário (soft delete)"""
        return await self.repo.deactivate_user(user_id)

    async def hard_delete_user(self, user_id: UuidType) -> bool:
        """Remove permanentemente um usuário"""
        return await self.repo.hard_delete(user_id)

    async def activate_user(self, user_id: UuidType) -> User:
        """Ativa um usuário"""
        return await self.repo.activate_user(user_id)

    async def get_users_by_type(self, user_type: UserType) -> List[User]:
        """Busca usuários por tipo específico"""
        return await self.repo.get_by_type(user_type)