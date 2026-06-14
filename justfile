default:
    @just --list

sync:
    uv sync --group dev

test:
    uv run pytest

run:
    uv run game-budget serve --data ./data --host 0.0.0.0 --port 8080

init:
    uv run game-budget init --data ./data --sample samples/boys.dat

docker-build:
    docker compose build

docker-up:
    docker compose up --build
