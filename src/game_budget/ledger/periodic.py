from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class DailyAllowanceLine:
    account: str
    amount: Decimal


@dataclass(frozen=True)
class DailyBlock:
    period: str
    lines: tuple[DailyAllowanceLine, ...]
    balancing_account: str

    def render(self) -> str:
        parts = [f"~ {self.period}"]
        for line in self.lines:
            parts.append(f"\t{line.account}\t\t\t${line.amount:.2f}")
        parts.append(f"\t{self.balancing_account}")
        return "\n".join(parts) + "\n"


_AMOUNT_RE = re.compile(r"^\$(?P<amount>-?\d+(?:\.\d+)?)$")
_DAILY_HEADER_RE = re.compile(r"^~\s+(?P<period>.+)$")


def parse_daily_block(text: str) -> DailyBlock | None:
    lines = text.splitlines()
    if not lines or not lines[0].startswith("~"):
        return None

    header = _DAILY_HEADER_RE.match(lines[0])
    if not header:
        return None

    allowance_lines: list[DailyAllowanceLine] = []
    balancing_account = "Assets"

    for raw in lines[1:]:
        if not raw.strip():
            break
        if raw.startswith("~") or re.match(r"^\d{4}/", raw):
            break

        parts = raw.split("\t")
        parts = [p.strip() for p in parts if p.strip()]
        if len(parts) == 1:
            balancing_account = parts[0]
            continue
        if len(parts) >= 2:
            account = parts[0]
            amount_match = _AMOUNT_RE.match(parts[1])
            if amount_match:
                allowance_lines.append(
                    DailyAllowanceLine(
                        account=account,
                        amount=Decimal(amount_match.group("amount")),
                    )
                )

    if not allowance_lines:
        return None

    return DailyBlock(
        period=header.group("period").strip(),
        lines=tuple(allowance_lines),
        balancing_account=balancing_account,
    )


def split_daily_block(content: str) -> tuple[str, DailyBlock | None, str]:
    """Return (before, daily_block, after)."""
    lines = content.splitlines(keepends=True)
    if not lines or not lines[0].startswith("~"):
        return content, None, ""

    end = 1
    while end < len(lines):
        line = lines[end]
        stripped = line.strip()
        if not stripped:
            end += 1
            break
        if line.startswith("~") or re.match(r"^\d{4}/", stripped):
            break
        end += 1

    block_text = "".join(lines[:end])
    rest = "".join(lines[end:])
    return "", parse_daily_block(block_text.rstrip("\n")), rest.lstrip("\n")


def replace_daily_block(content: str, block: DailyBlock) -> str:
    _, existing, rest = split_daily_block(content)
    if existing is None:
        return block.render() + content
    return block.render() + rest
