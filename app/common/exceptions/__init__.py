"""
Exceções personalizadas para a aplicação
Importações centralizadas para facilitar o uso
"""

# Base exceptions
from .base_exceptions import (
    FrontnixException,
    EntityNotFoundError,
    EntityAlreadyExistsError,
    DatabaseError
)

# Validation exceptions
from .validation_exceptions import (
    ValidationError,
    BusinessRuleError,
    convert_validation_to_http_exception,
    convert_business_rule_to_http_exception
)

# HTTP Exception Handler centralizado
from .http_exception_handler import convert_to_http_exception

# User exceptions
from .user_exceptions import (
    UserNotFoundError,
    UserAlreadyExistsError
)

# Telephone Number exceptions
from .telephone_number_exceptions import (
    TelephoneNumberNotFoundError,
    TelephoneNumberAlreadyExistsError
)

# Veículo exceptions
from .veiculo_exceptions import (
    VeiculoNotFoundError,
    VeiculoAlreadyExistsError
)

# Abastecimento exceptions
from .abastecimento_exceptions import (
    AbastecimentoNotFoundError,
    AbastecimentoAlreadyExistsError
)

# Manutenção exceptions
from .manutencao_exceptions import (
    ManutencaoNotFoundError,
    ManutencaoAlreadyExistsError
)

__all__ = [
    # Base
    "FrontnixException",
    "EntityNotFoundError",
    "EntityAlreadyExistsError",
    "DatabaseError",
    
    # Validation
    "ValidationError",
    "BusinessRuleError",
    
    # HTTP Handler
    "convert_to_http_exception",
    
    # User
    "UserNotFoundError",
    "UserAlreadyExistsError",
    
    # Telephone Number
    "TelephoneNumberNotFoundError",
    "TelephoneNumberAlreadyExistsError",
    
    # Veículo
    "VeiculoNotFoundError",
    "VeiculoAlreadyExistsError",
    
    # Abastecimento
    "AbastecimentoNotFoundError",
    "AbastecimentoAlreadyExistsError",
    
    # Manutenção
    "ManutencaoNotFoundError",
    "ManutencaoAlreadyExistsError",
]
