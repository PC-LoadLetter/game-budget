# Getting started

Step-by-step guide for a new household. No prior Game Budget or ledger-cli experience required.

**Related:** [Operations](operations.md) · [Troubleshooting](troubleshooting.md) · [Application overview](application.md)

## What you need

| Requirement | Notes |
|-------------|-------|
| A home computer or NAS | Linux, macOS, or Windows with [Docker Desktop](https://www.docker.com/products/docker-desktop/) |
| Docker Compose | Included with Docker Desktop; on Linux, install the `docker compose` plugin |
| Port **8080** free | Or change the port mapping in `docker-compose.yml` |
| LAN devices | Phones, tablets, or PCs on the same Wi‑Fi — only a browser is needed |

The app is designed for a **trusted home network**. The kiosk page has no login; anyone on your LAN can log purchases. Only `/admin` is password-protected.

## Install

```bash
git clone <repository-url> game-budget
cd game-budget
mkdir -p data
docker compose up --build -d
```

The first build may take a few minutes. The `data/` folder holds your journal and settings and persists across restarts.

### Find your host address

On the machine running Docker:

```bash
# Linux
hostname -I | awk '{print $1}'

# macOS
ipconfig getifaddr en0
```

Open the kiosk from another device: `http://<that-ip>:8080`

If the page does not load, see [Troubleshooting](troubleshooting.md#cannot-reach-the-kiosk-from-a-phone-or-tablet).

---

## Path A — Fresh household (no existing ledger)

Use this when you are starting from zero.

### 1. Start the app

```bash
mkdir -p data
docker compose up --build -d
```

On first run the app creates a default `journal.dat` with two placeholder children and a $5/day allowance each. You will customize names and budgets next.

### 2. Secure admin

1. Open `http://<host-ip>:8080/admin`
2. Log in with password **`admin`**
3. Scroll to **Change admin password** and set a new password

### 3. Set daily budgets

On the admin page, set **Daily budget** and optional **Savings cron ($/day)** for each child, then click **Save settings**.

Savings cron moves that amount from a child's wallet into savings once per day (when the app is running).

### 4. Customize child names (if needed)

The admin UI edits budgets but **cannot add or rename children in v1**. To use your own names:

1. Stop the app: `docker compose down`
2. Edit `data/journal.dat` — change the names in the `~ Daily` block at the top:

   ```
   ~ Daily
       Alice           $5.00
       Bob             $5.00
       Assets
   ```

3. Edit `data/config.yaml` — update the `children:` list to match (names and colors)
4. Start again: `docker compose up -d`

See [Application overview — account naming](application.md#account-naming) if you need ledger details.

### 5. First-run checklist

- [ ] Admin password changed from `admin`
- [ ] Daily budgets set for each child
- [ ] Kiosk URL bookmarked on family devices (`http://<host-ip>:8080`)
- [ ] Test purchase logged and balance updated
- [ ] **Export journal** from admin works (backup sanity check)

### 6. Optional — custom background

In admin, set **Background image path** to a URL served by the app, e.g. `/static/my-photo.jpg`, after placing your image in `src/game_budget/web/static/` and rebuilding the image — or mount a static files volume if you customize the deployment.

Default background is `/static/default-bg.svg` (included in the image).

---

## Path B — Migrating an existing ledger

Use this if you already have a ledger-cli journal from the legacy Flask app or another install.

### 1. Install and start

```bash
git clone <repository-url> game-budget
cd game-budget
mkdir -p data
docker compose up --build -d
```

You do **not** need to copy the file into `data/` first.

### 2. Import

1. Open `http://<host-ip>:8080/admin` and log in (`admin` / then change password)
2. Under **Import ledger**, choose your file (any filename — `.dat`, `.ledger`, `.txt`)
3. Click **Import** — the current journal is backed up to `journal.dat.bak`

### 3. Verify

1. Open the kiosk (`/`) and confirm wallet and savings balances look correct
2. Adjust daily budgets in admin if needed (rewrites the `~ Daily` header in the journal)
3. Export a copy and keep it somewhere safe

If you prefer the filesystem route instead of import:

```bash
docker compose down
cp /path/to/your-ledger.dat data/journal.dat
docker compose up -d
```

---

## Daily use

| Who | URL | What they do |
|-----|-----|----------------|
| Kids / family | `/` | Check balances, log purchases |
| Parents | `/admin` | Budgets, savings cron, import/export, settings |

**Logging a purchase:** pick date, seller (Steam, Epic, etc.), game name, buyer, and cost. Submit — the page reloads with updated balances.

**Insufficient balance:** the purchase is rejected unless **Allow overdraft** is enabled in admin.

---

## Known limitations (v1)

- **Two-child kiosk layout** — the balance dashboard is optimized for two children side by side. With one child, balances may not display above the form (you can still log purchases). See [roadmap](roadmap.md) for UI improvements.
- **No admin UI to add/remove children** — edit `journal.dat` and `config.yaml` manually, or import a prepared journal.
- **No HTTPS by default** — fine on a trusted LAN; see [Operations — HTTPS](operations.md#https-optional) if you want TLS.

---

## Next steps

- [Operations](operations.md) — backup, upgrade, logs
- [Troubleshooting](troubleshooting.md) — common problems
- [Smoke test](smoke-test.md) — verify a install end-to-end
