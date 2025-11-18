import os
import joblib
import numpy as np

BASE_PATH = "/app/models/modelos_frota/"


# ----------------------------------------
#      UTILITÁRIOS DE ARQUIVOS
# ----------------------------------------

def get_model_paths(placa: str):
    folder = os.path.join(BASE_PATH, placa)
    return {
        "folder": folder,
        "model": os.path.join(folder, "modelo.joblib"),
        "limits": os.path.join(folder, "limites.joblib"),
        "historico": os.path.join(folder, "historico.npy"),
    }


def ensure_folder(placa: str):
    paths = get_model_paths(placa)
    os.makedirs(paths["folder"], exist_ok=True)
    return paths


# ----------------------------------------
#         ATUALIZAÇÃO ONLINE
# ----------------------------------------

def update_model_online(placa: str, media_calculada: float):
    """
    Atualiza o "modelo" incrementalmente.
    Usa estatística simples (média e desvio) até você evoluir depois.
    """

    paths = ensure_folder(placa)
    hist_file = paths["historico"]

    # Carrega histórico
    if os.path.exists(hist_file):
        historico = list(np.load(hist_file))
    else:
        historico = []

    # Adiciona a nova média
    historico.append(media_calculada)

    # Salva histórico atualizado
    np.save(hist_file, np.array(historico))

    # Só salva limites quando houver histórico suficiente
    if len(historico) >= 10:
        media_hist = float(np.mean(historico))
        std_hist = float(np.std(historico))

        limites = {
            "media": media_hist,
            "std": std_hist,
            "limite_sup": media_hist + 3 * std_hist,
            "limite_inf": media_hist - 3 * std_hist,
        }

        joblib.dump(limites, paths["limits"])

    return True


# ----------------------------------------
#       DETECÇÃO DE ANOMALIAS
# ----------------------------------------

def detect_anomaly(placa: str, media_informada: float):
    paths = get_model_paths(placa)

    # Se não há limites salvos, ainda não tem modelo treinado
    if not os.path.exists(paths["limits"]):
        return {
            "placa": placa,
            "media_historica": None,
            "std_historico": None,
            "limite_inferior": None,
            "limite_superior": None,
            "media_informada": media_informada,
            "anomalia": False,
            "rmse": None,
            "age": None,
            "motivo": "Ainda não há histórico suficiente para treinar o modelo."
        }

    limites = joblib.load(paths["limits"])
    media_hist = limites["media"]
    std_hist = limites["std"]
    limite_inf = limites["limite_inf"]
    limite_sup = limites["limite_sup"]

    # AGE – distância absoluta entre a média informada e a média histórica
    age = abs(media_informada - media_hist)

    # Desvio padrão médio → similar ao RMSE
    rmse = std_hist

    # Anomalia se estourou limite inferior ou superior
    is_anomalia = media_informada < limite_inf or media_informada > limite_sup

    return {
        "placa": placa,
        "media_historica": media_hist,
        "std_historico": std_hist,
        "limite_inferior": limite_inf,
        "limite_superior": limite_sup,
        "media_informada": media_informada,
        "anomalia": is_anomalia,
        "rmse": rmse,
        "age": age
    }



# -----------------------------------------------------
#     🔥 PADRÃO PARA INTEGRAR COM SUAS ROTAS ATUAIS
# -----------------------------------------------------

def check_anomaly(payload: dict):
    placa = payload["placa"]

    # Se já veio a média calculada no payload, usa ela
    if "media_calculada" in payload and payload["media_calculada"] is not None:
        media = payload["media_calculada"]
    else:
        # Se não veio, calcula temporariamente (km/litros)
        if payload.get("litros_usados", 0) > 0:
            media = payload["km"] / payload["litros_usados"]
        else:
            raise ValueError("Não foi possível calcular a média para verificar anomalia.")

    return detect_anomaly(placa, media)



def predict_consumption(payload: dict):
    placa = payload["placa"]
    paths = get_model_paths(placa)

    # Sem histórico → sem previsão
    if not os.path.exists(paths["historico"]):
        return {
            "previsao": None,
            "rmse": None,
            "age": None
        }

    historico = list(np.load(paths["historico"]))

    if len(historico) < 2:
        # Não existe variação → RMSE impossível calcular
        return {
            "previsao": float(np.mean(historico)),
            "rmse": None,
            "age": None
        }

    media_hist = float(np.mean(historico))
    rmse = float(np.sqrt(np.mean((np.array(historico) - media_hist) ** 2)))

    # Se o usuário mandou litros e km para prever o AGE
    if "km" in payload and "litros_usados" in payload:
        if payload["litros_usados"] > 0:
            media_atual = payload["km"] / payload["litros_usados"]
            age = abs(media_atual - media_hist)
        else:
            age = None
    else:
        age = None

    return {
        "previsao": media_hist,
        "rmse": rmse,
        "age": age
    }

