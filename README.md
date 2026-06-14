# Game Budget

Self-hosted LAN game allowance kiosk. Parents set daily budgets; kids log purchases
from phones or PCs on the home network. Accounting uses a plain-text **ledger-cli**
journal (`boys.dat`) for full compatibility with the existing Flask app.

**Documentation:** [Application overview](docs/application.md) · [Roadmap](docs/roadmap.md)

## Quick start (Docker)

```bash
mkdir -p data
cp /path/to/your/boys.dat data/boys.dat   # or start fresh via init inside container
docker compose up --build
```

Open `http://<host>:8080` on your LAN.

Default admin password on first run: `admin` (change at `/admin`).

## Development

```bash
nix develop   # optional: Python, ledger, uv, just
uv sync --group dev
uv run game-budget init --data ./data
cp samples/boys.dat data/boys.dat         # optional test journal
uv run game-budget serve --data ./data --host 0.0.0.0
```

## Data layout

| Path | Purpose |
|------|---------|
| `data/boys.dat` | Ledger journal (mount as Docker volume) |
| `data/config.yaml` | Child colors, budgets, admin hash |

Back up `./data` before upgrades.

## License

MIT — see [LICENSE](LICENSE). ledger-cli is BSD 3-Clause — see [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES).
