# Troubleshooting

## Container exits immediately (Podman / Docker)

```bash
podman ps -a
podman logs game-budget
```

| Log message | Fix |
|-------------|-----|
| `Directory '.../web/static' does not exist` | Pull latest code, then `podman build --no-cache -t game-budget .` (stale build cache skipped packaging web assets) |
| Image not found | Run `podman build -t game-budget .` first |

The image build should pass a check that `web/static` and `web/templates` exist after `pip install`. If the build succeeds but the container still crashes, see logs and [Getting started — Podman](getting-started.md#podman-without-docker-compose).

## Cannot reach the kiosk from a phone or tablet

1. **Same network** — the device must be on the same Wi‑Fi or LAN as the host (not mobile data).
2. **Correct IP** — use the host machine's LAN address, not `localhost` or `127.0.0.1`.
3. **Port** — default is `8080`; confirm `docker compose ps` shows `0.0.0.0:8080->8080/tcp`.
4. **Firewall** — on Linux, allow inbound 8080 for the Docker bridge or disable the rule temporarily to test:

   ```bash
   sudo ufw allow 8080/tcp
   ```

5. **Docker Desktop (Windows/Mac)** — ensure the container is running and port forwarding is enabled in Docker settings.

## Admin login fails

- Default password on **first run only** is `admin` (lowercase).
- If you already changed it, reset by editing `data/config.yaml` — delete the `admin_password_hash` line, restart the app, log in with `admin`, and set a new password. (The app regenerates the hash on next `ensure_config`.)

## Balances show $0.00 or an error page

- **Docker:** ledger-cli is bundled in the image; rebuild if you customized the Dockerfile without `ledger`.
- **Bare metal:** install `ledger` and confirm `ledger --version` works.
- **Bad journal:** import or restore a known-good `journal.dat`. Check container logs: `docker compose logs game-budget`.

## "Insufficient wallet balance" (or savings)

Expected behavior — the selected buyer account does not have enough funds. Options:

- Choose a different buyer (e.g. spend from savings)
- Wait for daily allowance to accrue (ledger-cli expands the `~ Daily` block)
- Enable **Allow overdraft** in admin (not recommended for everyday use)

## Import did not change gamer names

Import replaces `journal.dat` but `config.yaml` may still list old gamers. After import:

1. Check the `~ Daily` block at the top of `journal.dat`
2. Restart the app or visit admin — `ensure_config` syncs from the journal
3. If names are still wrong, edit `config.yaml` `gamers:` to match the journal and restart (legacy `children:` is still read on load)

## Background image missing or broken

- Default is `/static/default-bg.svg` (shipped in the image).
- If admin points to a custom path, the file must exist under the app's static directory inside the container unless you mount it.
- An invalid path shows a plain dark background — harmless.

## Purchases logged but balances unchanged

- Hard-refresh the kiosk page (balances update on reload after submit).
- Confirm the transaction appears at the end of `journal.dat`.
- Run manually: `docker compose exec game-budget ledger -f /data/journal.dat balance Assets:GamerName --flat`

## Single gamer — no balance banner

The kiosk dashboard layout expects **two gamers** for the large balance row. With one gamer configured, the purchase form still works; balances may not display prominently. This is a known v1 limitation — see [roadmap](roadmap.md).

## Container exits immediately

```bash
docker compose logs game-budget
```

Common causes: port already in use, corrupt `config.yaml` (invalid YAML), or permission denied on `./data`. Fix and `docker compose up -d` again.

## Getting help

When reporting an issue, include:

- Docker vs bare metal
- Relevant log lines (`docker compose logs --tail=50 game-budget`)
- Whether the problem is kiosk, admin, or balances
- Redact `admin_password_hash` and `secret_key` from any `config.yaml` snippets
