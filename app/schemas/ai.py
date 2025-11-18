from pydantic import BaseModel
from typing import Optional


# -------------------------
# 🔥 ANOMALIA
# -------------------------
class AnomalyRequest(BaseModel):
    placa: str
    media: float


class AnomalyResponse(BaseModel):
    placa: str
    media_historica: Optional[float]
    std_historico: Optional[float]
    limite_inferior: Optional[float]
    limite_superior: Optional[float]
    media_informada: float
    anomalia: bool
    rmse: Optional[float]
    age: Optional[float]
    motivo: Optional[str] = None



# -------------------------
# 🔥 PREVISÃO
# -------------------------
class PredictRequest(BaseModel):
    placa: str


class PredictResponse(BaseModel):
    placa: str
    previsao_km_por_litro: Optional[float]
    rmse_estimado: Optional[float]
    age_estimado: Optional[float] = None
