import os
import joblib
import numpy as np

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

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
#         TREINAMENTO ROBUSTO
# ----------------------------------------

def train_robust_model(placa: str, historico: np.ndarray):
    """
    Treina um modelo de detecção de anomalias robusto
    usando IsolationForest em cima da média de consumo.
    Salva o modelo em modelo.joblib e atualiza limites.joblib.
    """

    paths = ensure_folder(placa)

    # reshape para (n amostras, 1 feature)
    X = historico.reshape(-1, 1)

    # Padronização
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Modelo de anomalia
    iso = IsolationForest(
        n_estimators=200,
        contamination=0.05,   # ~5% de anomalias esperadas
        random_state=42
    )
    iso.fit(X_scaled)

    media_hist = float(np.mean(historico))
    std_hist = float(np.std(historico))

    # Limites estatísticos mais realistas
    limite_sup = media_hist + 1.5 * std_hist
    limite_inf = max(media_hist - 1.5 * std_hist, 0.1)

    modelo = {
        "scaler": scaler,
        "iso": iso,
        "media": media_hist,
        "std": std_hist,
        "limite_sup": limite_sup,
        "limite_inf": limite_inf,
    }

    # Salva modelo completo
    joblib.dump(modelo, paths["model"])

    # Também salva limites em arquivo separado, para compatibilidade
    limites = {
        "media": media_hist,
        "std": std_hist,
        "limite_sup": limite_sup,
        "limite_inf": limite_inf,
    }
    joblib.dump(limites, paths["limits"])


# ----------------------------------------
#         ATUALIZAÇÃO ONLINE
# ----------------------------------------

def update_model_online(placa: str, media_calculada: float):
    """
    Atualiza o "modelo" incrementalmente.
    Agora guarda histórico e, quando tiver dados suficientes,
    treina / atualiza o modelo robusto (IsolationForest).
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
    historico_np = np.array(historico, dtype=float)
    np.save(hist_file, historico_np)

    # Só treina modelo robusto quando houver histórico suficiente
    if len(historico_np) >= 30:  # você pode ajustar esse mínimo
        train_robust_model(placa, historico_np)

    return True


# ----------------------------------------
#       DETECÇÃO DE ANOMALIAS
# ----------------------------------------

def detect_anomaly(placa: str, media_informada: float):
    paths = get_model_paths(placa)
    model_path = paths["model"]
    limits_path = paths["limits"]

    # Se não existe limites E não existe modelo → IA não está pronta
    if not os.path.exists(model_path) and not os.path.exists(limits_path):
        return {
            "placa": placa,
            "anomalia": False,
            "motivo": "Ainda não há histórico suficiente para treinar o modelo.",
            "media_informada": media_informada
        }

    # Carregar limites sempre (base estatística)
    limites = joblib.load(limits_path)
    media_hist = limites["media"]
    std_hist = limites["std"]
    limite_inf = limites["limite_inf"]
    limite_sup = limites["limite_sup"]

    # Verificação estatística (regra fixa)
    limite_alerta = media_informada < limite_inf or media_informada > limite_sup

    # Se NÃO existe modelo robusto (IsolationForest) → usar só limites
    if not os.path.exists(model_path):
        return {
            "placa": placa,
            "media_historica": media_hist,
            "std_historico": std_hist,
            "limite_inferior": limite_inf,
            "limite_superior": limite_sup,
            "media_informada": media_informada,
            "anomalia": limite_alerta,
            "motivo": "Detecção baseada apenas em limites estatísticos."
        }

    # Carregar modelo robusto (modelo + scaler)
    modelo = joblib.load(model_path)
    scaler = modelo["scaler"]
    iso = modelo["iso"]

    # Rodar IsolationForest
    X = np.array([[media_informada]])
    X_scaled = scaler.transform(X)
    label = iso.predict(X_scaled)[0]

    # Anomalia final = limites OU modelo
    is_anomalia = limite_alerta or (label == -1)

    return {
        "placa": placa,
        "media_historica": media_hist,
        "std_historico": std_hist,
        "limite_inferior": limite_inf,
        "limite_superior": limite_sup,
        "media_informada": media_informada,
        "anomalia": is_anomalia,
        "motivo": "Limites ou modelo detectaram anomalia."
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

    historico_np = np.array(historico, dtype=float)
    media_hist = float(np.mean(historico_np))
    rmse = float(np.sqrt(np.mean((historico_np - media_hist) ** 2)))

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
