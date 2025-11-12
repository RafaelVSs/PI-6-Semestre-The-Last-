from uuid import UUID
from .base_exceptions import FrontnixException
"""
Exceções específicas para entidade Manutenção
"""

class ManutencaoNotFoundError(FrontnixException):
    
    def __init__(self, message: str = "Manutenção não encontrada"):
        super().__init__(
            message=message,
            code="ENTITY_NOT_FOUND",
            context={"entity_name": "Manutencao"}
        )
    
    @staticmethod
    def by_id(manutencao_id: UUID) -> "ManutencaoNotFoundError":
        return ManutencaoNotFoundError(f"Manutenção com ID {manutencao_id} não encontrada")
    
    @staticmethod
    def by_ordem_servico(ordem_servico: str) -> "ManutencaoNotFoundError":
        return ManutencaoNotFoundError(f"Manutenção com ordem de serviço {ordem_servico} não encontrada")


class ManutencaoAlreadyExistsError(FrontnixException):
    """Exceção para manutenção já existente"""
    
    def __init__(self, message: str = "Manutenção já existe"):
        super().__init__(
            message=message,
            code="ENTITY_ALREADY_EXISTS",
            context={"entity_name": "Manutencao"}
        )
    
    @staticmethod
    def by_ordem_servico(ordem_servico: str) -> "ManutencaoAlreadyExistsError":
        return ManutencaoAlreadyExistsError(f"Manutenção com ordem de serviço {ordem_servico} já está cadastrada")
