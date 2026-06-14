# Smoke test checklist

Run this after install or before sharing the project with another household. Requires Docker and `ledger` on the host (optional, for manual balance checks).

## Setup

```bash
cd game-budget
rm -rf data          # only on a throwaway test — skips if you have live data
mkdir -p data
cp samples/fixture.dat data/journal.dat
docker compose up --build -d
```

Wait until `docker compose ps` shows the service running.

## Checks

| # | Step | Expected |
|---|------|----------|
| 1 | Open `http://localhost:8080` | Kiosk loads; wallet and savings balances visible for two gamers |
| 2 | Open `/admin`, login `admin` | Admin settings page loads |
| 3 | Change admin password | Can log in with new password |
| 4 | Set Beta daily budget to `7.00`, save | Redirects to admin; `~ Daily` in `data/journal.dat` shows `$7.00` for Beta |
| 5 | Kiosk: log Steam purchase for Alpha, $1.00 | Redirects to `/`; Alpha wallet decreases by $1.00 |
| 6 | Admin → Export journal | Downloads `journal.dat` |
| 7 | `docker compose exec game-budget ledger -E -f /data/journal.dat --budget bal --invert` | Gamer wallet on kiosk matches budget balance for that name |
| 8 | `docker compose down` then `docker compose up -d` | Balances unchanged after restart |
| 9 | `uv run pytest` (on host, from project root) | All tests pass |

## Import test (optional)

| # | Step | Expected |
|---|------|----------|
| 10 | Admin → Import a copy of `samples/fixture.dat` | Success; `journal.dat.bak` created |
| 11 | Kiosk balances | Match pre-import values |

## Automated tests

```bash
uv sync --group dev
uv run pytest -q
```

The balance test in `tests/test_journal_compat.py` is skipped if `ledger` is not installed on the host.

## Sign-off

Record environment when marking an install good:

- [ ] Date: ___________
- [ ] Host OS: ___________
- [ ] Docker version: ___________
- [ ] All checklist rows passed
