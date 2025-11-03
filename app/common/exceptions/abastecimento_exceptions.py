"""
Exceções específicas para entidade Abastecimento
"""
from uuid import UUID
from .base_exceptions import FrontnixException


class AbastecimentoNotFoundError(FrontnixException):
    """Exceção para abastecimento não encontrado"""
    
    def __init__(self, message: str = "Abastecimento não encontrado"):
        super().__init__(
            message=message,
            code="ENTITY_NOT_FOUND",
            context={"entity_name": "Abastecimento"}
        )
    
    @staticmethod
    def by_id(abastecimento_id: UUID) -> "AbastecimentoNotFoundError":
        return AbastecimentoNotFoundError(f"Abastecimento com ID {abastecimento_id} não encontrado")
    
    @staticmethod
    def by_numero_nota(numero_nota: str) -> "AbastecimentoNotFoundError":
        return AbastecimentoNotFoundError(f"Abastecimento com número da nota {numero_nota} não encontrado")


class AbastecimentoAlreadyExistsError(FrontnixException):
    """Exceção para abastecimento já existente"""
    
    def __init__(self, message: str = "Abastecimento já existe"):
        super().__init__(
            message=message,
            code="ENTITY_ALREADY_EXISTS",
            context={"entity_name": "Abastecimento"}
        )
    
    @staticmethod
    def by_numero_nota(numero_nota: str) -> "AbastecimentoAlreadyExistsError":
        return AbastecimentoAlreadyExistsError(f"Abastecimento com número da nota {numero_nota} já está cadastrado")
