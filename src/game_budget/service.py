from __future__ import annotations

import shutil
from datetime import date
from decimal import Decimal
from pathlib import Path

from game_budget.config import AppConfig, ensure_config, journal_path
from game_budget.ledger.balances import savings_display, wallet_display
from game_budget.ledger.journal import append_journal, read_journal
from game_budget.ledger.transactions import TransactionRequest


def init_data(data: Path, sample_journal: Path | None = None) -> None:
    data.mkdir(parents=True, exist_ok=True)
    journal = journal_path(data)
    if not journal.exists():
        if sample_journal and sample_journal.exists():
            shutil.copy(sample_journal, journal)
        else:
            journal.write_text(
                "~ Daily\n\tCleanrig\t\t\t$5.00\n\tFalafel\t\t\t$5.00\n\tAssets\n",
                encoding="utf-8",
            )
    ensure_config(data)


def savings_cron_entry(gamer: str, amount: Decimal, txn_date: date | None = None) -> str:
    d = (txn_date or date.today()).strftime("%Y/%m/%d")
    return (
        f"{d} cron\n"
        f"    {gamer}:Savings                            ${amount:.2f}\n"
        f"    Expenses:Gaming:Saving\n"
    )


def maybe_run_savings_cron(data: Path, config: AppConfig) -> None:
    journal = journal_path(data)
    if not journal.exists():
        return
    today = date.today().strftime("%Y/%m/%d")
    content = read_journal(journal)
    for gamer in config.gamers:
        if gamer.savings_cron <= 0:
            continue
        marker = f"{today} cron\n    {gamer.name}:Savings"
        if marker in content:
            continue
        append_journal(journal, savings_cron_entry(gamer.name, gamer.savings_cron))


def kiosk_balances(data: Path, config: AppConfig) -> dict[str, dict[str, Decimal]]:
    journal = journal_path(data)
    result: dict[str, dict[str, Decimal]] = {}
    for gamer in config.gamers:
        result[gamer.name] = {
            "wallet": wallet_display(journal, gamer.name),
            "savings": savings_display(journal, gamer.name),
        }
    return result


def validate_sufficient_funds(
    data: Path,
    config: AppConfig,
    req: TransactionRequest,
) -> None:
    if config.allow_overdraft:
        return
    journal = journal_path(data)
    balances = kiosk_balances(data, config)

    if req.seller == "Savings":
        if not req.buyer.endswith(" Savings"):
            raise ValueError("Invalid savings buyer")
        gamer = req.buyer[: -len(" Savings")]
        if balances[gamer]["wallet"] < req.cost:
            raise ValueError("Insufficient wallet balance for savings deposit")
        return

    if req.buyer.endswith(" Savings"):
        gamer = req.buyer[: -len(" Savings")]
        if balances[gamer]["savings"] < req.cost:
            raise ValueError("Insufficient savings balance")
        return

    if req.buyer in balances:
        if balances[req.buyer]["wallet"] < req.cost:
            raise ValueError("Insufficient wallet balance")
