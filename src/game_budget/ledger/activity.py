from __future__ import annotations

import math
import subprocess
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from game_budget.ledger.balances import LedgerError, budget_balance_map


def _break_even_line(name: str, balance: Decimal, daily_budget: Decimal) -> str:
    if daily_budget <= 0:
        return ""
    days = math.ceil(-balance / daily_budget)
    target = date.today() + timedelta(days=days)
    day_label = target.strftime("%a %b %d")
    unit = "day" if days == 1 else "days"
    return f"{name} breaks even in {days} {unit} on {day_label}\n"


def break_even_report(journal: Path, daily_budgets: dict[str, Decimal]) -> str:
    balances = budget_balance_map(journal)
    lines: list[str] = []
    for name, daily in daily_budgets.items():
        balance = balances.get(name)
        if balance is not None and balance < 0:
            line = _break_even_line(name, balance, daily)
            if line:
                lines.append(line)
    return "".join(lines)


def register_report(journal: Path, *, days: int = 14) -> str:
    result = subprocess.run(
        [
            "ledger",
            "-f",
            str(journal),
            "-b",
            f"last {days} days",
            "-S",
            "-date",
            "-E",
            "reg",
            "not",
            "Assets",
            "and",
            "not",
            "Mom",
            "and",
            "not",
            "Savings",
            "and",
            "not",
            "Saving",
            "--format",
            "\t%(date)\t%8.8(amount)\t%50.50(account)\n",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise LedgerError(result.stderr.strip() or "ledger register failed")
    return result.stdout.replace(":Gaming", "")


def kiosk_activity(
    journal: Path,
    daily_budgets: dict[str, Decimal],
    *,
    days: int = 14,
) -> str:
    header = break_even_report(journal, daily_budgets)
    register = register_report(journal, days=days).strip()
    if not register:
        register = f"No purchases in the last {days} days."
    return header + register + ("\n" if not register.endswith("\n") else "")
