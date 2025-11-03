from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.enums import UserStatus, UserType
from app.common.exceptions.user_exceptions import UserNotFoundError


class UserRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_data: UserCreate) -> User:
        """Cria um novo usuário no banco de dados"""
        db_user = User(
            name=user_data.name,
            lastName=user_data.lastName,
            email=user_data.email,
            password=user_data.password,
            cpf=user_data.cpf,
            type=user_data.type,
            status=user_data.status
        )
        
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def get_by_id(self, user_id: UUID) -> User:
        """Busca um usuário pelo ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundError.by_id(user_id)
        return user

    async def get_by_email(self, email: str) -> User:
        """Busca um usuário pelo email"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundError.by_email(email)
        return user

    async def get_by_cpf(self, cpf: str) -> User:
        """Busca um usuário pelo CPF"""
        result = await self.db.execute(
            select(User).where(User.cpf == cpf)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundError.by_cpf(cpf)
        return user

    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[UserStatus] = None,
        user_type: Optional[UserType] = None,
        search: Optional[str] = None
    ) -> List[User]:
        """Lista usuários com filtros e paginação"""
        query = select(User)
        
        # Filtro por status
        if status is not None:
            query = query.where(User.status == status)
        
        # Filtro por tipo de usuário
        if user_type is not None:
            query = query.where(User.type == user_type)
            
        # Filtro por busca (nome, email)
        if search:
            search_filter = or_(
                User.name.ilike(f"%{search}%"),
                User.lastName.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
            query = query.where(search_filter)

        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def count(
        self,
        status: Optional[UserStatus] = None,
        user_type: Optional[UserType] = None,
        search: Optional[str] = None
    ) -> int:
        """Conta o número total de usuários com filtros"""
        query = select(func.count(User.id))

        if status is not None:
            query = query.where(User.status == status)
        
        if user_type is not None:
            query = query.where(User.type == user_type)
        
        if search:
            search_filter = or_(
                User.name.ilike(f"%{search}%"),
                User.lastName.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.cpf.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
        
        result = await self.db.execute(query)
        return result.scalar()

    async def update(self, user_id: UUID, user_data: UserUpdate) -> User:
        """Atualiza um usuário existente"""
        db_user = await self.get_by_id(user_id)
        if not db_user:
            raise UserNotFoundError.by_id(user_id)

        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)

        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def hard_delete(self, user_id: UUID) -> bool:
        """Remove permanentemente um usuário do banco"""
        db_user = await self.get_by_id(user_id)
        if not db_user:
            raise UserNotFoundError.by_id(user_id)

        await self.db.delete(db_user)
        await self.db.commit()
        return True

    async def activate_user(self, user_id: UUID) -> User:
        """Ativa um usuário (muda status para ATIVO)"""
        db_user = await self.get_by_id(user_id)
        if not db_user:
            raise UserNotFoundError.by_id(user_id)

        db_user.status = UserStatus.ATIVO
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def deactivate_user(self, user_id: UUID) -> User:
        """Desativa um usuário (muda status para INATIVO)"""
        db_user = await self.get_by_id(user_id)
        if not db_user:
            raise UserNotFoundError.by_id(user_id)

        db_user.status = UserStatus.INATIVO
        await self.db.commit()
        await self.db.refresh(db_user)
        return True

    async def get_by_type(self, user_type: UserType) -> List[User]:
        """Busca usuários por tipo específico"""
        result = await self.db.execute(
            select(User)
            .where(User.type == user_type)
            .where(User.status == UserStatus.ATIVO)
            .order_by(User.name)
        )
        return result.scalars().all()

    async def exists_email(self, email: str, exclude_user_id: Optional[UUID] = None) -> bool:
        """Verifica se já existe um usuário com o email"""
        query = select(User.id).where(User.email == email)

        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def exists_cpf(self, cpf: str, exclude_user_id: Optional[UUID] = None) -> bool:
        """Verifica se já existe um usuário com o CPF"""
        query = select(User.id).where(User.cpf == cpf)
        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
