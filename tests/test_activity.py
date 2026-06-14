from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from game_budget.config import JOURNAL_FILENAME
from game_budget.ledger.activity import break_even_report, kiosk_activity, register_report
from game_budget.ledger.transactions import TransactionRequest, format_transaction, sanitize_game

SAMPLE = Path(__file__).resolve().parents[1] / "samples" / JOURNAL_FILENAME


def test_sanitize_game_strips_colons_and_apostrophes():
    assert sanitize_game("Hollow: Knight's Tale") == "Hollow Knights Tale"


def test_format_transaction_sanitizes_game_detail():
    req = TransactionRequest(
        txn_date=date(2026, 6, 14),
        seller="Steam",
        game="foo:bar'baz",
        buyer="Falafel",
        cost=Decimal("9.99"),
    )
    entry = format_transaction(req)
    assert "Falafel:Gaming:foobarbaz" in entry


@pytest.mark.skipif(not Path("/usr/bin/ledger").exists() and not Path("/run/current-system/sw/bin/ledger").exists(),
                    reason="ledger-cli not installed")
def test_register_report_strips_gaming_suffix():
    if not SAMPLE.exists():
        pytest.skip("sample journal missing")
    report = register_report(SAMPLE, days=730)
    assert ":Gaming" not in report
    assert "Falafel" in report


@pytest.mark.skipif(not Path("/usr/bin/ledger").exists() and not Path("/run/current-system/sw/bin/ledger").exists(),
                    reason="ledger-cli not installed")
def test_kiosk_activity_empty_window_message():
    if not SAMPLE.exists():
        pytest.skip("sample journal missing")
    activity = kiosk_activity(SAMPLE, {"Falafel": Decimal("5"), "Cleanrig": Decimal("5")}, days=14)
    if "breaks even" not in activity:
        assert "No purchases in the last 14 days." in activity


@pytest.mark.skipif(not Path("/usr/bin/ledger").exists() and not Path("/run/current-system/sw/bin/ledger").exists(),
                    reason="ledger-cli not installed")
def test_break_even_report_is_string():
    if not SAMPLE.exists():
        pytest.skip("sample journal missing")
    report = break_even_report(SAMPLE, {"Falafel": Decimal("4"), "Cleanrig": Decimal("5")})
    assert isinstance(report, str)
