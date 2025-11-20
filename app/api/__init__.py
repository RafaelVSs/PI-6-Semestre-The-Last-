from fastapi import APIRouter
from .routers import (
    auth_router,
    users_router,
    telephone_router,
    refuel_router,
    vehicle_router,
    maintenance_router,
    alert_routers,
    ai_router,
    dashboard_routers
    
)

# Criar router principal para API (prefixo /api/v1)
api_router = APIRouter()

# Lista de todos os routers da API
routers = [
    auth_router,
    users_router,
    telephone_router,
    refuel_router,
    vehicle_router,
    maintenance_router,
    alert_routers,
    ai_router,
    dashboard_routers
]

# Incluir todos os routers
for router in routers:
    api_router.include_router(router)
