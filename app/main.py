from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import settings

from app.api.routers.home import router as home_router
from app.api.routers.auth import router as auth_router
from app.api.routers.users import router as users_router
from app.api.routers.telephone_number import router as telephone_router
from app.api.routers.refuel import router as refuel_router
from app.api.routers.vehicle import router as vehicle_router
from app.api.routers.maintenance import router as maintenance_router
from app.api.routers.ai import router as ai_router
from app.api.routers.alert import router as alert_router

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

# CORS ------------------------------------------------------------------

origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui rota raiz ------------------------------------------------------

app.include_router(home_router)

# 🔥 INCLUSÃO DE TODOS OS ROUTERS MANUALMENTE
# (agora que seu __init__.py exporta todos via __all__)
# Obs: você NÃO precisa mais do api_router agrupado.
# Agora é explícito e claro.
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(users_router, prefix="/api/v1/users")
app.include_router(telephone_router, prefix="/api/v1/telephone")
app.include_router(refuel_router, prefix="/api/v1/refuel")
app.include_router(vehicle_router, prefix="/api/v1/vehicle")
app.include_router(maintenance_router, prefix="/api/v1/maintenance")
app.include_router(ai_router, prefix="/api/v1/ai")  # ✅ NOVO
app.include_router(alert_router, prefix="/api/v1/alerts")


# ----------------------------------------------------------------------

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

# ----------------------------------------------------------------------

# Startup ---------------------------------------------------------------

async def startup_event():
    print("Aplicação FastAPI iniciada com sucesso!")
    print(f"Acesse a documentação da API em http://127.0.0.1:8080/docs")
