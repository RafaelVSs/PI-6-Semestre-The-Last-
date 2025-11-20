from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date
from typing import List, Optional

from app.models.vehicle import Vehicle
from app.models.refuel import Refuel
from app.schemas.dashboard import DashboardMetricsResponse, ChartData

class DashboardRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard_metrics(
        self,
        placas: Optional[List[str]],
        data_inicial: Optional[date],
        data_final: Optional[date]
    ) -> DashboardMetricsResponse:
        
        # ---------------------------
        # MÉTRICA 1: Total de Veículos
        # ---------------------------
        query = select(func.count(Vehicle.id))
        if placas:
            query = query.where(Vehicle.placa.in_(placas))

        total_veiculos = (await self.db.execute(query)).scalar() or 0

        # ---------------------------
        # MÉTRICAS DE COMBUSTÍVEL
        # ---------------------------
        refuel_query = select(Refuel)

        if placas:
            refuel_query = refuel_query.where(Refuel.placa.in_(placas))
        if data_inicial:
            refuel_query = refuel_query.where(Refuel.data >= data_inicial)
        if data_final:
            refuel_query = refuel_query.where(Refuel.data <= data_final)

        refuels = (await self.db.execute(refuel_query)).scalars().all()

        total_litros = sum([float(r.litros) for r in refuels])
        custo_total = sum([float(r.valor_total) for r in refuels])

        # ---------------------------
        # GRÁFICO: Gasto por mês
        # ---------------------------
        gasto_por_mes: dict[str, float] = {}

        for r in refuels:
            mes = r.data.strftime("%b")  # Jan, Fev, Mar...
            gasto_por_mes.setdefault(mes, 0)
            gasto_por_mes[mes] += float(r.valor_total)

        gasto_data = [
            ChartData(name=mes, gasto=valor)
            for mes, valor in gasto_por_mes.items()
        ]

        # ---------------------------
        # GRÁFICO: Consumo Médio por Veículo
        # ---------------------------
        consumo_por_veiculo: dict[str, List[float]] = {}

        for r in refuels:
            if r.media:
                consumo_por_veiculo.setdefault(r.placa, [])
                consumo_por_veiculo[r.placa].append(float(r.media))

        consumo_data = [
            ChartData(name=placa, consumo=sum(valores) / len(valores))
            for placa, valores in consumo_por_veiculo.items()
        ]

        return DashboardMetricsResponse(
            totalVeiculos=total_veiculos,
            custoTotalCombustivel=custo_total,
            mediaConsumoFrota=(sum([cd.consumo for cd in consumo_data]) / len(consumo_data)) if consumo_data else 0,
            gastoData=gasto_data,
            vehicleConsumptionData=consumo_data,
            veiculoMaisEconomico=max(consumo_data, key=lambda x: x.consumo, default=None),
            veiculoMaisConsome=min(consumo_data, key=lambda x: x.consumo, default=None),
            alertas=[]
        )
