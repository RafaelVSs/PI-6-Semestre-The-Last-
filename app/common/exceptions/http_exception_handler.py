"""
Conversor centralizado de exceções de domínio para HTTPException
"""
from fastapi import HTTPException
from http import HTTPStatus
from typing import Union


# === Mapeamento de códigos para status HTTP ===
EXCEPTION_HTTP_STATUS_MAP = {
    "ENTITY_NOT_FOUND": HTTPStatus.NOT_FOUND,
    "ENTITY_ALREADY_EXISTS": HTTPStatus.CONFLICT,
    "DATABASE_ERROR": HTTPStatus.INTERNAL_SERVER_ERROR,
    "VALIDATION_ERROR": HTTPStatus.UNPROCESSABLE_ENTITY,
    "BUSINESS_RULE_ERROR": HTTPStatus.BAD_REQUEST,
}


def convert_to_http_exception(exception: Exception) -> HTTPException:
    """
    Converte exceções de domínio para HTTPException de forma genérica
    
    Suporta:
    - ValidationError
    - BusinessRuleError
    - FrontnixException (e suas subclasses)
    - Qualquer exceção com atributos .message e .code
    """
    from .validation_exceptions import ValidationError, BusinessRuleError, \
        convert_validation_to_http_exception, convert_business_rule_to_http_exception
    from .base_exceptions import FrontnixException
    
    # Validação e BusinessRule errors (mantém lógica específica)
    if isinstance(exception, ValidationError):
        return convert_validation_to_http_exception(exception)
    elif isinstance(exception, BusinessRuleError):
        return convert_business_rule_to_http_exception(exception)
    
    # FrontnixException (genérica baseada em código)
    elif isinstance(exception, FrontnixException):
        status_code = EXCEPTION_HTTP_STATUS_MAP.get(
            exception.code, 
            HTTPStatus.INTERNAL_SERVER_ERROR
        )
        
        detail = {
            "message": exception.message,
            "code": exception.code,
            "context": exception.context
        }
        
        return HTTPException(status_code=status_code, detail=detail)
    
    # Fallback para exceções não mapeadas
    else:
        return HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail={
                "message": "Erro interno do servidor",
                "code": "INTERNAL_ERROR"
            }
        )
