from pydantic import BaseModel
from typing import List, Optional


class ChartData(BaseModel):
    name: str
    gasto: Optional[float] = None
    consumo: Optional[float] = None


class DashboardMetricsResponse(BaseModel):
    totalVeiculos: int
    abastecimentosRecentes: int
    custoTotalCombustivel: float
    mediaConsumoFrota: float
    gastoData: List[ChartData]
    vehicleConsumptionData: List[ChartData]
    veiculoMaisEconomico: Optional[ChartData]
    veiculoMaisConsome: Optional[ChartData]
