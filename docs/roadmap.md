# Roadmap

Living plan for Game Budget. Update this document when priorities change or work ships.

For how the app works today, see [Application overview](application.md).

## Status summary

| Phase | Theme | Status |
|-------|-------|--------|
| 0 | Scaffold, Docker, ledger core | **Done** |
| 1 | Config, `~ Daily` sync, transaction writers | **Done** |
| 2 | Kiosk UI, admin UI | **Done** |
| 3 | Import/export, compatibility tests | **Done** |
| 4 | Documentation, ops polish | **Done** |
| 4b | Responsive kiosk (mobile / tablet) | **Planned** |
| 5 | Gamers + responsive kiosk | **Planned** |
| — | Other v2 features | **Planned** |

## Now — documentation and polish

- [x] Application overview in `docs/`
- [x] Roadmap in `docs/`
- [x] Expand README with links to docs and backup/upgrade notes
- [x] Getting started guide (fresh + migration paths)
- [x] Operations guide (backup, upgrade, HTTPS sketch)
- [x] Troubleshooting guide
- [x] Smoke-test checklist
- [x] Default background image shipped (`/static/default-bg.svg`)

## Next — sharing and ops

- [ ] Publish Docker image to GHCR (or similar) for one-command pulls
- [ ] GitHub Actions: test on push, optional image publish
- [ ] Bare-metal install guide referencing `deploy/game-budget.service`
- [ ] First-release tagging and CHANGELOG

## Next — responsive kiosk layout (mobile / tablet)

**Problem today:** Balance banners use inline `font-size: 75px` in a fixed four-column HTML table (`kiosk.html`) — amounts and names overflow or wrap badly on phones and small tablets. The activity feed is ~30px with no breakpoint. `background-attachment: fixed` is janky on iOS Safari. The purchase form is already fluid; the balance header and activity block are not.

**Target:** A comfortable kiosk on phone and tablet for existing **two-gamer** households, without waiting for multi-gamer admin or setup flows.

- [ ] Move balance styles from inline HTML into `kiosk.css`; scale type with `clamp()` and/or `@media` breakpoints (desktop can keep the large legacy look)
- [ ] Replace the balance `<table>` with a flex/grid card layout — two cards side-by-side on tablet, stacked on phone (wallet + savings per gamer)
- [ ] Scale `.activity-feed` on narrow viewports; preserve `pre-wrap` / `word-break` so register lines stay readable
- [ ] Background image: avoid `background-attachment: fixed` on mobile; tune `background-size` / `background-position` for narrow screens
- [ ] Smoke-test on phone and tablet (portrait and landscape); note any admin-page gaps separately

**Deferred to Phase 5:** 1-gamer and 3+ gamer layouts, looping all gamers in the template, dropping `_kiosk_columns()` — see [Gamers and kiosk layout](#later--v2-gamers-and-kiosk-layout).

## Later — v2: Gamers and kiosk layout

**Problem today:** First-run defaults and fallbacks embed author family names (`Cleanrig`, `Falafel`) in `service.py`, `config.py`, and `routes_kiosk.py`. The kiosk only renders balance banners when **two** gamers exist (`kiosk.html` `{% if left and right %}`). Admin can edit budgets but not names. New households must hand-edit `journal.dat` and `config.yaml`.

**Target:** Any household can configure **1, 2, 3, or more** gamers without editing ledger files. Kiosk layout adapts to gamer count on phone and desktop.

### Remove hardcoded defaults

- [ ] Replace `Cleanrig` / `Falafel` in `init_data()` default journal with neutral placeholders (e.g. `Gamer1`, `Gamer2`) or an empty `~ Daily` block until setup completes
- [ ] Remove `names = ["Cleanrig", "Falafel"]` fallback in `ensure_config()` — require setup flow or journal inference instead
- [ ] Remove `DEFAULT_GAMER_COLORS` name-specific map; use a small palette assigned by index
- [ ] Remove `_kiosk_columns()` Cleanrig/Falafel preference in `routes_kiosk.py`
- [x] Remove hardcoded gamer-name check in `transactions.py` `_gamer_from_buyer()`

### Gamer configuration (admin or first-run setup)

Implement **admin-first**; first-run setup as a redirect when `gamers` is empty.

| Approach | When | UX |
|----------|------|-----|
| **First-run setup** (`/admin/setup` or redirect when `gamers` empty) | Fresh install | Parent enters gamer names, daily budgets, colors; writes `config.yaml` + `~ Daily` block |
| **Admin gamer management** | Ongoing | Add / rename / remove / reorder gamers; syncs `config.yaml` and rewrites `~ Daily` |

- [ ] Add gamer — append to `config.gamers`, add `~ Daily` line, optional opening `Assets:{name}` balance (or start at $0)
- [ ] Rename gamer — update config + rewrite account prefixes in journal (or document as manual / import-only for v2.0)
- [ ] Remove gamer — remove from `~ Daily`, deactivate in config (preserve historical journal entries read-only)
- [ ] Validate names (no tabs, reasonable length, unique)
- [ ] On save: call existing `sync_daily_block()` in `config.py`

**Rename semantics:** Renaming accounts in an existing journal is hard (many historical postings). **v2.0 = add/remove + display names in config**; **rename in ledger = deferred or import-only** unless we scope account-alias mapping.

### Responsive kiosk layout (1 / 2 / 3+ gamers)

Builds on [responsive kiosk layout (mobile / tablet)](#next--responsive-kiosk-layout-mobile--tablet) when that ships first. Replace the fixed two-column table with a gamer-count-aware template:

- [ ] **1 gamer** — single balance card above form (fixes current blank banner bug)
- [ ] **2 gamers** — side-by-side cards on desktop/tablet, stacked on phone (not hardcoded Cleanrig/Falafel columns)
- [ ] **3+ gamers** — grid of cards (name, wallet, savings per gamer); scale font size down on small screens
- [ ] Drop `_kiosk_columns()`; pass `gamers` + `balances` only; template loops all gamers
- [ ] Optional: HTMX partial refresh on balance update (see also UI improvements below)

### Docs and tests

- [ ] Update `docs/getting-started.md` — remove manual journal editing for names once admin/setup ships
- [ ] Add tests: 1-gamer and 3-gamer config fixtures; `sync_daily_block` with N lines
- [ ] Update smoke-test checklist for multi-gamer grid

### Success criteria (v2 gamers)

- [ ] Fresh install: parent can set 1–N gamer names without touching `journal.dat` by hand
- [ ] Kiosk shows balances for every configured gamer on phone and desktop
- [ ] No author family names in application code defaults (samples/tests may keep example data)

## Later — v2 features

### Chores (earn credit)

The sample journal contains chore entries (negative `{Gamer}:Gaming` postings that credit the wallet). v1 preserves this history but provides no kiosk UI to record new chores.

- Admin or kiosk flow to post chore credits
- Validation against configured chore types or free-form amounts

### UI improvements

- HTMX partial refresh on the kiosk (balances without full page reload)
- Responsive layout: [mobile / tablet pass](#next--responsive-kiosk-layout-mobile--tablet) (near term), then [gamer-count layout](#responsive-kiosk-layout-1--2--3-gamers) (Phase 5)

### Optional accounting

- [x] Read-only register view (rolling 14-day activity feed on kiosk)
- Parent adjustment form (equity corrections without hand-editing the journal)

## Explicitly out of scope

These are intentional non-goals unless requirements change significantly:

- Multi-household or cloud-hosted SaaS
- Native mobile apps
- Payment processor / real-money integration
- Beancount or alternate accounting engines (incompatible with the ledger-cli journal format)
- Pure-Python replacement for ledger-cli (periodic `~ Daily` expansion is non-trivial)
- Gamer or parent PIN logins on the kiosk (LAN-trust model matches the legacy app)

## Success criteria (v1)

- [x] Kiosk shows wallet + savings balances matching ledger-cli for configured gamers
- [x] Form submit appends correct journal entries (purchase, savings deposit, spend from savings, hardware)
- [x] Admin can edit daily budgets (rewrites `~ Daily` block)
- [x] Export downloads `journal.dat`; import accepts any ledger file (backs up before replace)
- [x] `docker compose up` serves the kiosk with ledger-cli inside the container
- [x] README and docs sufficient for another household to adopt without author hand-holding

## How to use this roadmap

1. **Track in git** — This file is versioned with the code; update it in the same PR as feature work when practical.
2. **Issues for tasks** — Use GitHub Issues for granular work items; keep this file for themes and phases.
3. **Defer detail** — Design notes belong in `docs/application.md` or code; avoid duplicating the full original build plan here.
