from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.alert_service import AlertService
from app.schemas.alert import AlertCreate, AlertResolveUpdate, AlertResponse

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=list[AlertResponse])
async def list_alerts(
    id_veiculo: str | None = None,
    severity: str | None = None,
    resolved: bool | None = None,
    db: AsyncSession = Depends(get_db)
):
    service = AlertService(db)
    alerts = await service.list_alerts(id_veiculo, severity, resolved)
    return alerts


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
    service = AlertService(db)
    alert = await service.get_alert(alert_id)
    if not alert:
        raise HTTPException(404, "Alerta não encontrado")
    return alert


@router.post("/", response_model=AlertResponse)
async def create_alert(payload: AlertCreate, db: AsyncSession = Depends(get_db)):
    service = AlertService(db)
    alert = await service.create_alert(
        id_veiculo=payload.id_veiculo,
        id_abastecimento=payload.id_abastecimento,
        severity=payload.severity,
        message=payload.message
    )
    return alert


@router.patch("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(alert_id: str, payload: AlertResolveUpdate, db: AsyncSession = Depends(get_db)):
    service = AlertService(db)
    alert = await service.resolve_alert(alert_id, payload.resolved)
    if not alert:
        raise HTTPException(404, "Alerta não encontrado")
    return alert


@router.delete("/{alert_id}")
async def delete_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
    service = AlertService(db)
    alert = await service.delete_alert(alert_id)
    if not alert:
        raise HTTPException(404, "Alerta não encontrado")
    return {"message": "Alerta removido com sucesso"}
