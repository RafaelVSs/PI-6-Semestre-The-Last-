from uuid import UUID
from .base_exceptions import FrontnixException


class TelephoneNumberNotFoundError(FrontnixException):
    """Exceção para número de telefone não encontrado"""
    
    def __init__(self, message: str = "Número de telefone não encontrado"):
        super().__init__(
            message=message,
            code="ENTITY_NOT_FOUND",
            context={"entity_name": "TelephoneNumber"}
        )
    
    @staticmethod
    def by_id(tel_id: UUID) -> "TelephoneNumberNotFoundError":
        return TelephoneNumberNotFoundError(f"Número de telefone com ID {tel_id} não encontrado")
    
    @staticmethod
    def by_number(number: str) -> "TelephoneNumberNotFoundError":
        return TelephoneNumberNotFoundError(f"Número de telefone {number} não encontrado")


class TelephoneNumberAlreadyExistsError(FrontnixException):
    """Exceção para número de telefone já existente"""
    
    def __init__(self, message: str = "Número de telefone já existe"):
        super().__init__(
            message=message,
            code="ENTITY_ALREADY_EXISTS",
            context={"entity_name": "TelephoneNumber"}
        )
    
    @staticmethod
    def by_number(number: str) -> "TelephoneNumberAlreadyExistsError":
        return TelephoneNumberAlreadyExistsError(f"Número de telefone {number} já está cadastrado")
