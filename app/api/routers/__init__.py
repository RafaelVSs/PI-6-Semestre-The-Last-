from .home import router as home_router
from .auth import router as auth_router
from .users import router as users_router
from .telephone_number import router as telephone_router
from .refuel import router as refuel_router
from .vehicle import router as vehicle_router
from .maintenance import router as maintenance_router
from .ai import router as ai_router
from .alert import router as alert_routers


# Lista de todos os routers para exportação
__all__ = [
    "home_router",
    "auth_router",
    "users_router",
    "telephone_router", 
    "refuel_router",
    "vehicle_router",
    "maintenance_router",
    "ai_router",
    "alert_routers"
]