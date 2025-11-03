
FROM python:3.12-slim as builder

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY --from=builder /app/.venv /app/.venv

COPY app ./app
COPY create_tables.py ./
COPY run-api.sh ./

RUN chmod +x run-api.sh

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/healthcheck')" || exit 1

CMD ["./run-api.sh", "prod"]
