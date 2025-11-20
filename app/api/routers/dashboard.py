from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from typing import List, Optional

# ✔ CORRETO – seu get_db fica em app/core/database.py
from app.core.database import get_db

# ⚠ VERIFICAR NOME DO ARQUIVO: deve ser "dashboard_repository.py"
from app.repositories.dashboard_repository import DashboardRepository

# ✔ CORRETO – conforme arquivo que criamos antes
from app.schemas.dashboard import DashboardMetricsResponse

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

@router.get(
    "/metrics",
    response_model=DashboardMetricsResponse,
    summary="Retorna todas as métricas do Dashboard",
    description="Retorna métricas gerais, gráficos e estatísticas filtradas por placa e data."
)
async def dashboard_metrics(
    placas: Optional[List[str]] = Query(
        None,
        description="Lista de placas para filtrar"
    ),
    data_inicial: Optional[date] = Query(
        None,
        description="Data inicial para filtro (AAAA-MM-DD)"
    ),
    data_final: Optional[date] = Query(
        None,
        description="Data final para filtro (AAAA-MM-DD)"
    ),
    db: AsyncSession = Depends(get_db)
):
    repo = DashboardRepository(db)

    result = await repo.get_dashboard_metrics(
        placas=placas,
        data_inicial=data_inicial,
        data_final=data_final
    )

    return result
