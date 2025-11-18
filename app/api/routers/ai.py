from fastapi import APIRouter, HTTPException
from app.schemas.ai import AnomalyRequest, AnomalyResponse, PredictRequest, PredictResponse
from app.services.ai_service import predict_consumption, check_anomaly

router = APIRouter(prefix="/v1/ai", tags=["ai"])

# ----------------------------
# 🔥 1. DETECÇÃO DE ANOMALIA
# ----------------------------
@router.post("/anomaly", response_model=AnomalyResponse)
def detect_anomaly(payload: AnomalyRequest):
    try:
        result = check_anomaly(payload.dict())
        return result

    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")


# ----------------------------
# 🔥 2. PREVISÃO DE CONSUMO
# ----------------------------
@router.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest):
    try:
        r = predict_consumption(payload.dict())

        return {
            "placa": payload.placa,
            "previsao_km_por_litro": r["previsao"],
            "rmse_estimado": r["rmse"],
            "age_estimado": r["age"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")
