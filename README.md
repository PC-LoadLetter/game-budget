# Game Budget

Self-hosted LAN game allowance kiosk. Parents set daily budgets; kids log purchases
from phones or PCs on the home network. Accounting uses a plain-text **ledger-cli**
journal (`journal.dat`) compatible with the original Flask app format.

**Documentation:** [Application overview](docs/application.md) · [Roadmap](docs/roadmap.md)

## Quick start (Docker)

```bash
mkdir -p data
cp /path/to/your/journal.dat data/journal.dat   # or import via /admin later
docker compose up --build
```

Open `http://<host>:8080` on your LAN.

Default admin password on first run: `admin` (change at `/admin`).

## Development

```bash
nix develop   # optional: Python, ledger, uv, just
uv sync --group dev
uv run game-budget init --data ./data
cp samples/journal.dat data/journal.dat         # optional test journal
uv run game-budget serve --data ./data --host 0.0.0.0
```

## Data layout

| Path | Purpose |
|------|---------|
| `data/journal.dat` | Ledger journal (mount as Docker volume) |
| `data/config.yaml` | Child colors, budgets, admin hash |

Back up `./data` before upgrades. To migrate an existing ledger file, rename it to
`journal.dat` or use **Import ledger** on `/admin` (any filename accepted).

## License

MIT — see [LICENSE](LICENSE). ledger-cli is BSD 3-Clause — see [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES).
