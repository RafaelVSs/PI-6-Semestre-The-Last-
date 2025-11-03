from fastapi import HTTPException
from http import HTTPStatus
from typing import List, Optional, Dict, Any


class ValidationError(Exception):
    """Exceção para erros de validação de dados"""
    def __init__(self, message: str = "Erro de validação", 
                 field: Optional[str] = None, 
                 errors: Optional[List[str]] = None):
        self.message = message
        self.field = field
        self.errors = errors or []
        super().__init__(self.message)
    
    @classmethod
    def password_strength(cls, errors: List[str]) -> 'ValidationError':
        """Factory method para erros de força de senha"""
        message = f"Senha não atende aos critérios: {'; '.join(errors)}"
        return cls(message=message, field="password", errors=errors)
    
    @classmethod
    def invalid_field(cls, field: str, message: str) -> 'ValidationError':
        """Factory method para campo inválido"""
        return cls(message=f"Campo '{field}': {message}", field=field)
    
    @classmethod
    def required_field(cls, field: str) -> 'ValidationError':
        """Factory method para campo obrigatório"""
        return cls(message=f"Campo '{field}' é obrigatório", field=field)


class BusinessRuleError(Exception):
    """Exceção para violações de regras de negócio"""
    def __init__(self, message: str = "Regra de negócio violada", 
                 code: Optional[str] = None,
                 context: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.context = context or {}
        super().__init__(self.message)


def convert_validation_to_http_exception(exception: ValidationError) -> HTTPException:
    """Converte ValidationError para HTTPException"""
    detail = {
        "message": exception.message,
        "field": exception.field,
        "errors": exception.errors
    }
    
    return HTTPException(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        detail=detail
    )


def convert_business_rule_to_http_exception(exception: BusinessRuleError) -> HTTPException:
    """Converte BusinessRuleError para HTTPException"""
    detail = {
        "message": exception.message,
        "code": exception.code,
        "context": exception.context
    }
    
    return HTTPException(
        status_code=HTTPStatus.BAD_REQUEST,
        detail=detail
    )