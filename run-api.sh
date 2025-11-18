#!/bin/bash

set -e

# Modo de execução: dev (default) ou prod
MODE=${1:-dev}


if [ "$MODE" = "prod" ]; then
    echo "Iniciando a API em modo PRODUÇÃO na porta 8080..."
    # Produção: com workers e sem reload
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers 4 --log-level info
elif [ "$MODE" = "dev" ]; then
    echo "Iniciando a API em modo DESENVOLVIMENTO na porta 8080..."
    # Desenvolvimento: com reload
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload --log-level debug
else
    echo "Modo inválido. Use: ./run-api.sh [dev|prod]"
    exit 1
fi