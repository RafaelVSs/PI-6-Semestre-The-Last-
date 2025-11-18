from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.schemas.alert import AlertCreate


class AlertRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, alert_data: AlertCreate) -> Alert:
        alert = Alert(**alert_data.model_dump())
        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)
        return alert

    async def get_by_id(self, alert_id):
        query = select(Alert).where(Alert.id == alert_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def delete(self, alert: Alert):
        await self.db.delete(alert)
        await self.db.commit()

    async def update_resolved(self, alert: Alert, resolved: bool):
        alert.resolved = resolved
        await self.db.commit()
        await self.db.refresh(alert)
        return alert

    async def list(
        self,
        id_veiculo=None,
        severity=None,
        resolved=None
    ):
        query = select(Alert)

        if id_veiculo:
            query = query.where(Alert.id_veiculo == id_veiculo)

        if severity:
            query = query.where(Alert.severity == severity)

        if resolved is not None:
            query = query.where(Alert.resolved == resolved)

        query = query.order_by(Alert.created_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())
