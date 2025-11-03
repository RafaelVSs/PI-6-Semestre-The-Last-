"""
Exceções específicas para entidade Veículo (Caminhão)
"""
from uuid import UUID
from .base_exceptions import FrontnixException


class VeiculoNotFoundError(FrontnixException):
    """Exceção para veículo não encontrado"""
    
    def __init__(self, message: str = "Veículo não encontrado"):
        super().__init__(
            message=message,
            code="ENTITY_NOT_FOUND",
            context={"entity_name": "Veiculo"}
        )
    
    @staticmethod
    def by_id(veiculo_id: UUID) -> "VeiculoNotFoundError":
        return VeiculoNotFoundError(f"Veículo com ID {veiculo_id} não encontrado")
    
    @staticmethod
    def by_placa(placa: str) -> "VeiculoNotFoundError":
        return VeiculoNotFoundError(f"Veículo com placa {placa} não encontrado")
    
    @staticmethod
    def by_chassi(chassi: str) -> "VeiculoNotFoundError":
        return VeiculoNotFoundError(f"Veículo com chassi {chassi} não encontrado")


class VeiculoAlreadyExistsError(FrontnixException):
    """Exceção para veículo já existente"""
    
    def __init__(self, message: str = "Veículo já existe"):
        super().__init__(
            message=message,
            code="ENTITY_ALREADY_EXISTS",
            context={"entity_name": "Veiculo"}
        )
    
    @staticmethod
    def by_placa(placa: str) -> "VeiculoAlreadyExistsError":
        return VeiculoAlreadyExistsError(f"Veículo com placa {placa} já está cadastrado")
    
    @staticmethod
    def by_chassi(chassi: str) -> "VeiculoAlreadyExistsError":
        return VeiculoAlreadyExistsError(f"Veículo com chassi {chassi} já está cadastrado")
