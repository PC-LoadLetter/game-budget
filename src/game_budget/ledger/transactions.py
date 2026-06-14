from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from game_budget.ledger.journal import append_journal


@dataclass(frozen=True)
class TransactionRequest:
    txn_date: date
    seller: str
    game: str
    buyer: str
    cost: Decimal


def _format_amount(amount: Decimal) -> str:
    return f"${amount:.2f}"


def _child_from_buyer(buyer: str) -> str | None:
    if buyer.endswith(" Savings"):
        return buyer[: -len(" Savings")]
    if buyer in {"Falafel", "Cleanrig"}:
        return buyer
    return None


def format_transaction(req: TransactionRequest) -> str:
    date_str = req.txn_date.strftime("%Y/%m/%d")
    game = req.game.strip()
    cost = req.cost

    if req.seller == "Savings":
        child = _child_from_buyer(req.buyer)
        if child is None:
            raise ValueError(f"Invalid buyer for savings deposit: {req.buyer}")
        return (
            f"{date_str} Savings\n"
            f"    {child}:Savings                           {_format_amount(-cost)}\n"
            f"    Assets:{child}\n"
        )

    if req.buyer.endswith(" Savings"):
        child = req.buyer[: -len(" Savings")]
        payee = "spend savings" if req.seller in {"Steam", "Epic", "Other"} else req.seller
        detail = game or req.seller
        return (
            f"{date_str} {payee}\n"
            f"    {child}:Gaming:{detail}                     {_format_amount(cost)}\n"
            f"    {child}:Savings\n"
        )

    if req.buyer == "Hardware":
        detail = game or "purchase"
        return (
            f"{date_str} {req.seller}\n"
            f"    Hardware:Gaming:{detail}           {_format_amount(cost)}\n"
            f"    Assets:Hardware\n"
        )

    if req.buyer in {"Mom", "Dad"}:
        detail = game or req.seller
        return (
            f"{date_str} {req.seller}\n"
            f"    {req.buyer}:Gaming:{detail}                  {_format_amount(cost)}\n"
            f"    Assets:{req.buyer}\n"
        )

    child = req.buyer
    detail = game or req.seller
    return (
        f"{date_str} {req.seller}\n"
        f"        {child}:Gaming:{detail}    {_format_amount(cost)}\n"
        f"        Assets:{child}\n"
    )


def parse_cost(raw: str) -> Decimal:
    cleaned = raw.strip().replace("$", "").replace(",", "")
    if not cleaned:
        raise ValueError("Cost is required")
    try:
        amount = Decimal(cleaned)
    except InvalidOperation as exc:
        raise ValueError("Invalid cost amount") from exc
    if amount <= 0:
        raise ValueError("Cost must be positive")
    return amount


def post_transaction(journal: Path, req: TransactionRequest) -> None:
    append_journal(journal, format_transaction(req))
