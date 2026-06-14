from __future__ import annotations

from datetime import date as date_cls
from decimal import Decimal
from urllib.parse import quote

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from game_budget.auth import generate_csrf_token, validate_csrf_token
from game_budget.config import AppConfig, journal_path
from game_budget.ledger.activity import kiosk_activity
from game_budget.ledger.transactions import TransactionRequest, parse_cost, post_transaction
from game_budget.service import kiosk_balances, maybe_run_savings_cron, validate_sufficient_funds

router = APIRouter()

ACTIVITY_LOOKBACK_DAYS = 14


def _format_money(amount: Decimal) -> str:
    text = f"${amount:.2f}"
    if amount >= 0:
        return f"  {text} "
    return text


def _kiosk_columns(gamers: list) -> tuple[object | None, object | None]:
    by_name = {gamer.name: gamer for gamer in gamers}
    left = by_name.get("Cleanrig")
    right = by_name.get("Falafel")
    if left is None and gamers:
        left = gamers[0]
    if right is None and len(gamers) > 1:
        right = gamers[1] if gamers[1] != left else None
    return left, right


def _resolve_background_image(
    config: AppConfig,
    *,
    query_image: str | None = None,
    form_image: str | None = None,
) -> str:
    if form_image:
        return form_image
    if query_image:
        return query_image
    return config.background_image


def _kiosk_context(
    request: Request,
    *,
    error: str | None = None,
    today: str | None = None,
    form_image_file: str | None = None,
) -> dict:
    config = request.state.config
    data = request.app.state.data_dir
    gamers = config.gamers
    left, right = _kiosk_columns(gamers)
    balances = kiosk_balances(data, config)
    background_image = _resolve_background_image(
        config,
        query_image=request.query_params.get("image_file"),
        form_image=form_image_file,
    )
    daily_budgets = {gamer.name: gamer.daily_budget for gamer in gamers}
    activity = kiosk_activity(
        journal_path(data),
        daily_budgets,
        days=ACTIVITY_LOOKBACK_DAYS,
    )
    return {
        "gamers": gamers,
        "left": left,
        "right": right,
        "balances": balances,
        "format_money": _format_money,
        "csrf_token": generate_csrf_token(config),
        "today": today or date_cls.today().isoformat(),
        "background_image": background_image,
        "image_file": background_image,
        "activity": activity,
        "error": error,
    }


@router.get("/", response_class=HTMLResponse)
async def kiosk_get(request: Request):
    config = request.state.config
    data = request.app.state.data_dir
    maybe_run_savings_cron(data, config)
    return request.app.state.templates.TemplateResponse(
        request,
        "kiosk.html",
        _kiosk_context(request),
    )


@router.post("/", response_class=HTMLResponse)
async def kiosk_post(
    request: Request,
    csrf_token: str = Form(""),
    txn_date: str = Form(""),
    seller: str = Form(""),
    game: str = Form(""),
    buyer: str = Form(""),
    cost: str = Form(""),
    image_file: str = Form(""),
):
    config = request.state.config
    data = request.app.state.data_dir
    templates = request.app.state.templates
    form_image = image_file or None

    if not validate_csrf_token(config, csrf_token):
        return templates.TemplateResponse(
            request,
            "kiosk.html",
            _kiosk_context(
                request,
                error="Invalid form token; refresh and try again.",
                today=txn_date or None,
                form_image_file=form_image,
            ),
            status_code=400,
        )

    try:
        req = TransactionRequest(
            txn_date=date_cls.fromisoformat(txn_date),
            seller=seller,
            game=game,
            buyer=buyer,
            cost=parse_cost(cost),
        )
        validate_sufficient_funds(data, config, req)
        post_transaction(journal_path(data), req)
        maybe_run_savings_cron(data, config)
        bg = _resolve_background_image(
            config,
            query_image=request.query_params.get("image_file"),
            form_image=form_image,
        )
        return RedirectResponse(f"/?image_file={quote(bg, safe='/')}", status_code=303)
    except ValueError as exc:
        return templates.TemplateResponse(
            request,
            "kiosk.html",
            _kiosk_context(
                request,
                error=str(exc),
                today=txn_date,
                form_image_file=form_image,
            ),
            status_code=400,
        )
