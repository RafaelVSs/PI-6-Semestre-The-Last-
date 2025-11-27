from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from .core.config import settings

# Configurar logging para a aplicação
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
from .api import api_router
from .api.routers.home import router as home_router
from .common.exceptions import (
    FrontnixException,
    ValidationError,
    BusinessRuleError,
    convert_to_http_exception
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="API para controle de abastecimento de frotas de caminhões"
)

origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(home_router)

app.include_router(
    api_router,
    prefix="/api/v1"
)


# Exception Handlers Globais -------------------------------------------

@app.exception_handler(FrontnixException)
async def frontnix_exception_handler(request: Request, exc: FrontnixException):
    http_exc = convert_to_http_exception(exc)
    return JSONResponse(
        status_code=http_exc.status_code,
        content=http_exc.detail
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    http_exc = convert_to_http_exception(exc)
    return JSONResponse(
        status_code=http_exc.status_code,
        content=http_exc.detail
    )

@app.exception_handler(BusinessRuleError)
async def business_rule_exception_handler(request: Request, exc: BusinessRuleError):
    http_exc = convert_to_http_exception(exc)
    return JSONResponse(
        status_code=http_exc.status_code,
        content=http_exc.detail
    )


async def startup_event():
    print("Aplicação FastAPI iniciada com sucesso!")
    print(f"Acesse a documentação da API em http://127.0.0.1:8080/docs")
