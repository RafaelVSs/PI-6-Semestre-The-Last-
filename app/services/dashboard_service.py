from app.repositories.dashboard_repository import DashboardRepository


class DashboardService:
    def __init__(self, db):
        self.repo = DashboardRepository(db)

    async def get_dashboard_data(self):
        total_veiculos = await self.repo.total_veiculos()
        custo_total = await self.repo.custo_total_periodo()
        abastecimentos_rec = await self.repo.abastecimentos_recentes()
        media_frota = await self.repo.media_consumo_frota()

        gasto_mes = await self.repo.gasto_por_mes()
        consumo_veiculos = await self.repo.consumo_por_veiculo()

        veiculo_mais_eco = (
            max(consumo_veiculos, key=lambda x: x["consumo"])
            if consumo_veiculos else None
        )
        veiculo_mais_cons = (
            min(consumo_veiculos, key=lambda x: x["consumo"])
            if consumo_veiculos else None
        )

        return {
            "dashboardMetrics": {
                "totalVeiculos": total_veiculos,
                "abastecimentosRecentes": abastecimentos_rec,
                "custoTotalCombustivel": custo_total,
                "mediaConsumoFrota": media_frota,
            },
            "gastoData": gasto_mes,
            "vehicleConsumptionData": consumo_veiculos,
            "veiculoMaisEconomico": veiculo_mais_eco,
            "veiculoMaisConsome": veiculo_mais_cons,
        }
