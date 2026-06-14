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


def wallet_display(journal: Path, child: str) -> Decimal:
    return -ledger_balance(journal, f"Assets:{child}")


def savings_display(journal: Path, child: str) -> Decimal:
    return ledger_balance(journal, f"{child}:Savings")
