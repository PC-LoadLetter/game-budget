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
| 5 | Children + responsive kiosk | **Planned** |
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

## Later — v2: Children and kiosk layout

**Problem today:** First-run defaults and fallbacks embed author family names (`Cleanrig`, `Falafel`) in `service.py`, `config.py`, and `routes_kiosk.py`. The kiosk only renders balance banners when **two** children exist (`kiosk.html` `{% if left and right %}`). Admin can edit budgets but not names. New households must hand-edit `journal.dat` and `config.yaml`.

**Target:** Any household can configure **1, 2, 3, or more** children without editing ledger files. Kiosk layout adapts to child count on phone and desktop.

### Remove hardcoded defaults

- [ ] Replace `Cleanrig` / `Falafel` in `init_data()` default journal with neutral placeholders (e.g. `Child1`, `Child2`) or an empty `~ Daily` block until setup completes
- [ ] Remove `names = ["Cleanrig", "Falafel"]` fallback in `ensure_config()` — require setup flow or journal inference instead
- [ ] Remove `DEFAULT_CHILD_COLORS` name-specific map; use a small palette assigned by index
- [ ] Remove `_kiosk_columns()` Cleanrig/Falafel preference in `routes_kiosk.py`
- [ ] Remove dead `{"Falafel", "Cleanrig"}` check in `transactions.py` `_child_from_buyer()`

### Child configuration (admin or first-run setup)

Implement **admin-first**; first-run setup as a redirect when `children` is empty.

| Approach | When | UX |
|----------|------|-----|
| **First-run setup** (`/admin/setup` or redirect when `children` empty) | Fresh install | Parent enters child names, daily budgets, colors; writes `config.yaml` + `~ Daily` block |
| **Admin child management** | Ongoing | Add / rename / remove / reorder children; syncs `config.yaml` and rewrites `~ Daily` |

- [ ] Add child — append to `config.children`, add `~ Daily` line, optional opening `Assets:{name}` balance (or start at $0)
- [ ] Rename child — update config + rewrite account prefixes in journal (or document as manual / import-only for v2.0)
- [ ] Remove child — remove from `~ Daily`, deactivate in config (preserve historical journal entries read-only)
- [ ] Validate names (no tabs, reasonable length, unique)
- [ ] On save: call existing `sync_daily_block()` in `config.py`

**Rename semantics:** Renaming accounts in an existing journal is hard (many historical postings). **v2.0 = add/remove + display names in config**; **rename in ledger = deferred or import-only** unless we scope account-alias mapping.

### Responsive kiosk layout (1 / 2 / 3+ children)

Replace fixed two-column table layout with a child-count-aware template:

- [ ] **1 child** — single balance card above form (fixes current blank banner bug)
- [ ] **2 children** — keep side-by-side wallet/savings rows (current look, but driven by `children[0]` / `children[1]`, not names)
- [ ] **3+ children** — grid of cards (name, wallet, savings per child); scale font size down on small screens
- [ ] Drop `_kiosk_columns()`; pass `children` + `balances` only; template loops all children
- [ ] Basic responsive CSS (flex/grid + `max-width` media query) — no new JS framework required for v2.0
- [ ] Optional: HTMX partial refresh on balance update (see also UI improvements below)

### Docs and tests

- [ ] Update `docs/getting-started.md` — remove manual journal editing for names once admin/setup ships
- [ ] Add tests: 1-child and 3-child config fixtures; `sync_daily_block` with N lines
- [ ] Update smoke-test checklist for multi-child grid

### Success criteria (v2 children)

- [ ] Fresh install: parent can set 1–N child names without touching `journal.dat` by hand
- [ ] Kiosk shows balances for every configured child on phone and desktop
- [ ] No author family names in application code defaults (samples/tests may keep example data)

## Later — v2 features

### Chores (earn credit)

The sample journal contains chore entries (negative `{Child}:Gaming` postings that credit the wallet). v1 preserves this history but provides no kiosk UI to record new chores.

- Admin or kiosk flow to post chore credits
- Validation against configured chore types or free-form amounts

### UI improvements

- HTMX partial refresh on the kiosk (balances without full page reload)
- See [Children and kiosk layout](#later--v2-children-and-kiosk-layout) for responsive layout and child management

### Optional accounting

- Read-only register view (recent transactions per child)
- Parent adjustment form (equity corrections without hand-editing the journal)

## Explicitly out of scope

These are intentional non-goals unless requirements change significantly:

- Multi-household or cloud-hosted SaaS
- Native mobile apps
- Payment processor / real-money integration
- Beancount or alternate accounting engines (incompatible with the ledger-cli journal format)
- Pure-Python replacement for ledger-cli (periodic `~ Daily` expansion is non-trivial)
- Child or parent PIN logins on the kiosk (LAN-trust model matches the legacy app)

## Success criteria (v1)

- [x] Kiosk shows wallet + savings balances matching ledger-cli for configured children
- [x] Form submit appends correct journal entries (purchase, savings deposit, spend from savings, hardware)
- [x] Admin can edit daily budgets (rewrites `~ Daily` block)
- [x] Export downloads `journal.dat`; import accepts any ledger file (backs up before replace)
- [x] `docker compose up` serves the kiosk with ledger-cli inside the container
- [x] README and docs sufficient for another household to adopt without author hand-holding

## How to use this roadmap

1. **Track in git** — This file is versioned with the code; update it in the same PR as feature work when practical.
2. **Issues for tasks** — Use GitHub Issues for granular work items; keep this file for themes and phases.
3. **Defer detail** — Design notes belong in `docs/application.md` or code; avoid duplicating the full original build plan here.
