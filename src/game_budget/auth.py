from __future__ import annotations

from itsdangerous import BadSignature, URLSafeSerializer

from game_budget.config import AppConfig


def csrf_serializer(config: AppConfig) -> URLSafeSerializer:
    return URLSafeSerializer(config.secret_key, salt="game-budget-csrf")


def generate_csrf_token(config: AppConfig) -> str:
    return csrf_serializer(config).dumps("csrf")


def validate_csrf_token(config: AppConfig, token: str | None) -> bool:
    if not token:
        return False
    try:
        value = csrf_serializer(config).loads(token)
    except BadSignature:
        return False
    return value == "csrf"


SESSION_COOKIE = "game_budget_admin"


def admin_session_serializer(config: AppConfig) -> URLSafeSerializer:
    return URLSafeSerializer(config.secret_key, salt="game-budget-admin")


def create_admin_session(config: AppConfig) -> str:
    return admin_session_serializer(config).dumps({"admin": True})


def validate_admin_session(config: AppConfig, token: str | None) -> bool:
    if not token:
        return False
    try:
        payload = admin_session_serializer(config).loads(token)
    except BadSignature:
        return False
    return bool(payload.get("admin"))
