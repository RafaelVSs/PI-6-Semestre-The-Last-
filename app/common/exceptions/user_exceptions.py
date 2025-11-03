from uuid import UUID
from .base_exceptions import FrontnixException


class UserNotFoundError(FrontnixException):
    """Exceção para usuário não encontrado"""
    
    def __init__(self, message: str = "Usuário não encontrado"):
        super().__init__(
            message=message,
            code="ENTITY_NOT_FOUND",
            context={"entity_name": "User"}
        )
    
    @staticmethod
    def by_id(user_id: UUID) -> "UserNotFoundError":
        return UserNotFoundError(f"Usuário com ID {user_id} não encontrado")
    
    @staticmethod
    def by_email(email: str) -> "UserNotFoundError":
        return UserNotFoundError(f"Usuário com email {email} não encontrado")
    
    @staticmethod
    def by_cpf(cpf: str) -> "UserNotFoundError":
        return UserNotFoundError(f"Usuário com CPF {cpf} não encontrado")


class UserAlreadyExistsError(FrontnixException):
    """Exceção para usuário já existente"""
    
    def __init__(self, message: str = "Usuário já existe"):
        super().__init__(
            message=message,
            code="ENTITY_ALREADY_EXISTS",
            context={"entity_name": "User"}
        )
    
    @staticmethod
    def by_email(email: str) -> "UserAlreadyExistsError":
        return UserAlreadyExistsError(f"Usuário com email {email} já está cadastrado")
    
    @staticmethod
    def by_cpf(cpf: str) -> "UserAlreadyExistsError":
        return UserAlreadyExistsError(f"Usuário com CPF {cpf} já está cadastrado")
