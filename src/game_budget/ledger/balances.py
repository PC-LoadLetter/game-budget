from __future__ import annotations

import re
import subprocess
from decimal import Decimal
from pathlib import Path


class LedgerError(RuntimeError):
    pass


_BALANCE_LINE_RE = re.compile(
    r"^\s*\$(?P<amount>-?\d+(?:,\d{3})*(?:\.\d+)?)\s+(?P<account>\S+)\s*$"
)


def _parse_amount(raw: str) -> Decimal:
    return Decimal(raw.replace(",", ""))


def ledger_balance(journal: Path, account: str) -> Decimal:
    result = subprocess.run(
        ["ledger", "-f", str(journal), "balance", account, "--flat"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise LedgerError(result.stderr.strip() or "ledger balance failed")

    for line in result.stdout.splitlines():
        match = _BALANCE_LINE_RE.match(line)
        if match and match.group("account") == account:
            return _parse_amount(match.group("amount"))

    return Decimal("0")


def _budget_balance_map(journal: Path) -> dict[str, Decimal]:
    """Parse ``ledger --budget bal --invert`` output (matches legacy Flask kiosk)."""
    result = subprocess.run(
        [
            "ledger",
            "-E",
            "-f",
            str(journal),
            "--budget",
            "bal",
            "--invert",
            "--format",
            "%(account)      %(amount) ",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise LedgerError(result.stderr.strip() or "ledger budget balance failed")

    balances: dict[str, Decimal] = {}
    tokens = result.stdout.split()
    i = 0
    while i + 1 < len(tokens):
        account = tokens[i]
        amount_raw = tokens[i + 1]
        if amount_raw.startswith("$"):
            balances[account] = _parse_amount(amount_raw[1:])
            i += 2
        else:
            i += 1
    return balances


def budget_balance_map(journal: Path) -> dict[str, Decimal]:
    return _budget_balance_map(journal)


def wallet_display(journal: Path, gamer_name: str) -> Decimal:
    return _budget_balance_map(journal).get(gamer_name, Decimal("0"))


def savings_display(journal: Path, gamer_name: str) -> Decimal:
    return ledger_balance(journal, f"{gamer_name}:Savings")
