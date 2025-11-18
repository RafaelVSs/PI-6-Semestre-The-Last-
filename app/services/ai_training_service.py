import os
import joblib
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from math import sqrt

BASE_PATH = "/app/models/modelos_frota/"


def get_paths(placa: str):
    folder = os.path.join(BASE_PATH, placa)
    return {
        "folder": folder,
        "historico": os.path.join(folder, "historico.npy"),
        "model": os.path.join(folder, "modelo.joblib"),
        "limits": os.path.join(folder, "limites.joblib")
    }


def ensure_folder(placa: str):
    os.makedirs(get_paths(placa)["folder"], exist_ok=True)


class AITrainingService:

    def train_for_truck(self, placa: str):
        """Treina um modelo real (linear regression) baseado nas últimas médias."""
        ensure_folder(placa)
        paths = get_paths(placa)

        if not os.path.exists(paths["historico"]):
            return {"status": "sem histórico suficiente"}

        historico = np.load(paths["historico"])

        if len(historico) < 5:
            return {"status": "menos de 5 dados — não treina"}

        # -----------------------------
        #    REGRSSÃO LINEAR REAL
        # -----------------------------
        X = np.arange(len(historico)).reshape(-1, 1)  # 0…n
        y = historico

        modelo = LinearRegression()
        modelo.fit(X, y)

        # erro real
        pred = modelo.predict(X)
        rmse = sqrt(mean_squared_error(y, pred))

        # salva o modelo
        joblib.dump({
            "modelo": modelo,
            "rmse": rmse
        }, paths["model"])

        return {
            "status": "modelo treinado",
            "historico": historico.tolist(),
            "rmse": rmse
        }


def train_online_append(placa: str, media_calculada: float):
    """Adiciona no histórico, depois tenta treinar."""
    ensure_folder(placa)
    paths = get_paths(placa)

    # Carrega histórico antigo
    if os.path.exists(paths["historico"]):
        historico = list(np.load(paths["historico"]))
    else:
        historico = []

    historico.append(media_calculada)
    np.save(paths["historico"], np.array(historico))

    # tenta treinar automaticamente
    trainer = AITrainingService()
    return trainer.train_for_truck(placa)


def predict_with_model(placa: str):
    """Retorna previsão real + rmse."""

    paths = get_paths(placa)

    if not os.path.exists(paths["model"]):
        return None, None

    data = joblib.load(paths["model"])
    modelo = data["modelo"]
    rmse = data["rmse"]

    # previsão para o próximo índice
    historico = np.load(paths["historico"])
    X_next = [[len(historico)]]

    pred = modelo.predict(X_next)[0]

    return float(pred), float(rmse)
