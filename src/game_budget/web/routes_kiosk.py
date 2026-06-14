from __future__ import annotations

from datetime import date as date_cls
from decimal import Decimal

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from game_budget.auth import generate_csrf_token, validate_csrf_token
from game_budget.config import load_config
from game_budget.ledger.transactions import TransactionRequest, parse_cost, post_transaction
from game_budget.service import kiosk_balances, maybe_run_savings_cron, validate_sufficient_funds

router = APIRouter()


def _format_money(amount: Decimal) -> str:
    text = f"${amount:.2f}"
    if amount >= 0:
        return f"  {text} "
    return text


def _kiosk_columns(children: list) -> tuple[object | None, object | None]:
    by_name = {child.name: child for child in children}
    left = by_name.get("Cleanrig")
    right = by_name.get("Falafel")
    if left is None and children:
        left = children[0]
    if right is None and len(children) > 1:
        right = children[1] if children[1] != left else None
    return left, right


@router.get("/", response_class=HTMLResponse)
async def kiosk_get(request: Request):
    config = request.state.config
    data = request.app.state.data_dir
    maybe_run_savings_cron(data, config)
    balances = kiosk_balances(data, config)
    children = config.children
    left, right = _kiosk_columns(children)

    return request.app.state.templates.TemplateResponse(
        request,
        "kiosk.html",
        {
            "children": children,
            "left": left,
            "right": right,
            "balances": balances,
            "format_money": _format_money,
            "csrf_token": generate_csrf_token(config),
            "today": date_cls.today().isoformat(),
            "background_image": config.background_image,
            "error": None,
        },
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
):
    config = request.state.config
    data = request.app.state.data_dir
    templates = request.app.state.templates
    children = config.children
    left, right = _kiosk_columns(children)
    balances = kiosk_balances(data, config)

    if not validate_csrf_token(config, csrf_token):
        return templates.TemplateResponse(
            request,
            "kiosk.html",
            {
                "children": children,
                "left": left,
                "right": right,
                "balances": balances,
                "format_money": _format_money,
                "csrf_token": generate_csrf_token(config),
                "today": txn_date or date_cls.today().isoformat(),
                "background_image": config.background_image,
                "error": "Invalid form token; refresh and try again.",
            },
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
        post_transaction(data / "boys.dat", req)
        maybe_run_savings_cron(data, config)
        return RedirectResponse("/", status_code=303)
    except ValueError as exc:
        balances = kiosk_balances(data, config)
        return templates.TemplateResponse(
            request,
            "kiosk.html",
            {
                "children": children,
                "left": left,
                "right": right,
                "balances": balances,
                "format_money": _format_money,
                "csrf_token": generate_csrf_token(config),
                "today": txn_date,
                "background_image": config.background_image,
                "error": str(exc),
            },
            status_code=400,
        )
