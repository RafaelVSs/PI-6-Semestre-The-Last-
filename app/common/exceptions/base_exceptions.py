"""
Exceções base reutilizáveis para toda a aplicação
"""
from typing import Optional, Dict, Any
from uuid import UUID


class FrontnixException(Exception):
    """Exceção base para todas as exceções da aplicação"""
    def __init__(self, message: str, code: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.context = context or {}
        super().__init__(self.message)


class EntityNotFoundError(FrontnixException):
    """Exceção genérica para entidades não encontradas"""
    def __init__(self, entity_name: str, identifier_value: Any = None, identifier_name: str = "ID"):
        if identifier_value:
            message = f"{entity_name} com {identifier_name} '{identifier_value}' não encontrado"
        else:
            message = f"{entity_name} não encontrado"
        
        super().__init__(
            message=message,
            code="ENTITY_NOT_FOUND",
            context={
                "entity_name": entity_name,
                "identifier_name": identifier_name,
                "identifier_value": str(identifier_value) if identifier_value else None
            }
        )


class EntityAlreadyExistsError(FrontnixException):
    """Exceção genérica para entidades que já existem"""
    def __init__(self, entity_name: str, identifier_value: Any, identifier_name: str = "ID"):
        message = f"{entity_name} com {identifier_name} '{identifier_value}' já existe"
        
        super().__init__(
            message=message,
            code="ENTITY_ALREADY_EXISTS", 
            context={
                "entity_name": entity_name,
                "identifier_name": identifier_name,
                "identifier_value": str(identifier_value)
            }
        )


class DatabaseError(FrontnixException):
    """Exceção para erros de banco de dados"""
    def __init__(self, message: str = "Erro no banco de dados", operation: Optional[str] = None):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            context={"operation": operation} if operation else {}
        )
