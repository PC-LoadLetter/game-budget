# Operations

Backup, upgrade, and day-two tasks for a running Game Budget install.

## Backup

All state lives in the data directory (default `./data` next to `docker-compose.yml`).

| File | What it holds |
|------|----------------|
| `journal.dat` | Full transaction history and daily allowance |
| `config.yaml` | Gamer settings, admin password hash, secrets |

### Recommended backup

```bash
cd game-budget
docker compose down
tar czf "game-budget-backup-$(date +%Y%m%d).tar.gz" data/
docker compose up -d
```

Stopping the container avoids copying the journal mid-write. For a quick live backup, use **Export journal** on `/admin` — that downloads `journal.dat` while the app runs.

Keep backups off the same disk when possible (cloud drive, another machine).

### Restore

```bash
docker compose down
rm -rf data    # caution — destructive
tar xzf game-budget-backup-YYYYMMDD.tar.gz
docker compose up -d
```

Or replace only `journal.dat` / `config.yaml` from a backup tarball.

## Upgrade

```bash
cd game-budget
docker compose down
# back up data/ first
git pull
docker compose up --build -d
```

Your `data/` volume is unchanged across upgrades. If release notes mention config changes, diff your `config.yaml` against a fresh `game-budget init` output.

## Logs and status

```bash
docker compose ps
docker compose logs -f game-budget
```

## Restart

```bash
docker compose restart
```

## Change port

Edit `docker-compose.yml`:

```yaml
ports:
  - "9080:8080"   # host:container
```

Then `docker compose up -d` and use `http://<host>:9080`.

## HTTPS (optional)

Game Budget listens on HTTP inside the container. For TLS on your LAN or when exposing beyond the home network, put a reverse proxy in front.

### Caddy (example)

```caddy
game-budget.home.arpa {
    reverse_proxy localhost:8080
}
```

Caddy obtains certificates automatically when the hostname resolves and is reachable. For pure LAN use, many households skip HTTPS.

### nginx (example sketch)

```nginx
server {
    listen 443 ssl;
    server_name game-budget.home.arpa;

    ssl_certificate     /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Point family devices at `https://game-budget.home.arpa` after DNS or `/etc/hosts` is set up.

## Bare metal

For hosts without Docker:

1. Install Python 3.12+, [ledger-cli](https://www.ledger-cli.org/), and [uv](https://docs.astral.sh/uv/)
2. `uv sync` in the project directory
3. `uv run game-budget init --data /var/lib/game-budget`
4. Run via `uv run game-budget serve --data /var/lib/game-budget --host 0.0.0.0`

An example systemd unit is in [`deploy/game-budget.service`](../deploy/game-budget.service). Adjust paths and enable with `systemctl enable --now game-budget`.

## Data directory permissions

Restrict `data/` to the user running the service (`chmod 700 data` on Linux). The journal contains no payment card data but does reflect family spending habits.
