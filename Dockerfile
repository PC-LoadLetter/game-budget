FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ledger \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir .

EXPOSE 8080

ENV GAME_BUDGET_DATA=/data

CMD ["game-budget", "serve", "--host", "0.0.0.0", "--port", "8080", "--data", "/data"]
