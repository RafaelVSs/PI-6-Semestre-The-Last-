from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.alert_repository import AlertRepository
from app.schemas.alert import AlertCreate


class AlertService:

    def __init__(self, db: AsyncSession):
        self.repo = AlertRepository(db)

    async def create_alert(self, id_veiculo, id_abastecimento, severity, message):
        alert = AlertCreate(
            id_veiculo=id_veiculo,
            id_abastecimento=id_abastecimento,
            severity=severity,
            message=message
        )
        return await self.repo.create(alert)

    async def list_alerts(self, id_veiculo=None, severity=None, resolved=None):
        return await self.repo.list(id_veiculo, severity, resolved)

    async def get_alert(self, alert_id):
        return await self.repo.get_by_id(alert_id)

    async def resolve_alert(self, alert_id, resolved=True):
        alert = await self.repo.get_by_id(alert_id)
        if not alert:
            return None
        return await self.repo.update_resolved(alert, resolved)

    async def delete_alert(self, alert_id):
        alert = await self.repo.get_by_id(alert_id)
        if alert:
            await self.repo.delete(alert)
        return alert
