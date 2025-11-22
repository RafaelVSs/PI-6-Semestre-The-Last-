import os
import numpy as np
import joblib
from pprint import pprint

def read_historico():
    if not os.path.exists("historico.npy"):
        print("\n❌ historico.npy não encontrado na pasta atual!")
        return None

    data = np.load("historico.npy")
    print("\n===== HISTÓRICO (historico.npy) =====")
    print("Quantidade de valores:", len(data))
    print("Valores:", data)
    print("-------------------------------------")
    return data


def read_limites():
    if not os.path.exists("limites.joblib"):
        print("\n❌ limites.joblib não encontrado na pasta atual!")
        return None

    limites = joblib.load("limites.joblib")
    print("\n===== LIMITES (limites.joblib) =====")
    pprint(limites)
    print("-------------------------------------")
    return limites


def read_modelo():
    if not os.path.exists("modelo.joblib"):
        print("\n❌ modelo.joblib não encontrado na pasta atual!")
        return None

    modelo = joblib.load("modelo.joblib")

    print("\n===== MODELO (modelo.joblib) =====")

    # Lista as chaves do dicionário
    print("\nChaves armazenadas:")
    pprint(list(modelo.keys()))

    # Exibe valores comuns
    print("\nMÉDIA HISTÓRICA:", modelo.get("media"))
    print("DESVIO PADRÃO :", modelo.get("std"))
    print("LIMITE INF   :", modelo.get("limite_inf"))
    print("LIMITE SUP   :", modelo.get("limite_sup"))

    # Verifica scaler
    if "scaler" in modelo:
        print("\nScaler encontrado (StandardScaler).")
    else:
        print("\nNenhum scaler encontrado.")

    # Verifica IsolationForest
    if "iso" in modelo:
        print("Modelo IsolationForest encontrado!")
    else:
        print("Nenhum modelo IsolationForest encontrado.")

    print("-------------------------------------")
    return modelo


def main():
    print("\n📂 Lendo arquivos da pasta:")
    print(os.getcwd())
    print("=" * 60)

    read_historico()
    read_limites()
    read_modelo()


if __name__ == "__main__":
    main()
