from decimal import Decimal
from pathlib import Path

import pytest

from game_budget.config import JOURNAL_FILENAME
from game_budget.ledger.balances import savings_display, wallet_display
from game_budget.ledger.periodic import DailyAllowanceLine, DailyBlock, parse_daily_block, replace_daily_block


SAMPLE = Path(__file__).resolve().parents[1] / "samples" / JOURNAL_FILENAME


@pytest.mark.skipif(not Path("/usr/bin/ledger").exists() and not Path("/run/current-system/sw/bin/ledger").exists(),
                    reason="ledger-cli not installed")
def test_balances_match_sample():
    if not SAMPLE.exists():
        pytest.skip("sample journal missing")
    assert wallet_display(SAMPLE, "Falafel") == Decimal("8445.85")
    assert wallet_display(SAMPLE, "Cleanrig") == Decimal("7339.49")
    assert savings_display(SAMPLE, "Falafel") == Decimal("72.88")
    assert savings_display(SAMPLE, "Cleanrig") == Decimal("-0.10")


def test_parse_daily_block():
    text = "~ Daily\n\tFalafel\t\t\t$5.00\n\tCleanrig\t\t\t$5.00\n\tAssets\n"
    block = parse_daily_block(text)
    assert block is not None
    assert block.period == "Daily"
    assert len(block.lines) == 2
    assert block.lines[0].account == "Falafel"
    assert block.lines[0].amount == Decimal("5.00")


def test_replace_daily_block():
    original = "~ Daily\n\tFalafel\t\t\t$5.00\n\tAssets\n\n2026/01/01 Test\n"
    new_block = DailyBlock(
        period="Daily",
        lines=(DailyAllowanceLine("Falafel", Decimal("7.00")),),
        balancing_account="Assets",
    )
    updated = replace_daily_block(original, new_block)
    assert updated.startswith("~ Daily")
    assert "$7.00" in updated
    assert "2026/01/01 Test" in updated
