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
| 4 | Documentation, ops polish | **In progress** |
| — | v2 features | **Planned** |

## Now — documentation and polish

- [x] Application overview in `docs/`
- [x] Roadmap in `docs/`
- [x] Expand README with links to docs and backup/upgrade notes
- [ ] Document HTTPS reverse-proxy setup (Caddy/nginx sketch)
- [ ] Smoke-test checklist for Docker + sample `journal.dat`

## Next — sharing and ops

- [ ] Publish Docker image to GHCR (or similar) for one-command pulls
- [ ] GitHub Actions: test on push, optional image publish
- [ ] Bare-metal install guide referencing `deploy/game-budget.service`
- [ ] First-release tagging and CHANGELOG

## Later — v2 features

### Chores (earn credit)

The sample journal contains chore entries (negative `{Child}:Gaming` postings that credit the wallet). v1 preserves this history but provides no kiosk UI to record new chores.

- Admin or kiosk flow to post chore credits
- Validation against configured chore types or free-form amounts

### UI improvements

- HTMX partial refresh on the kiosk (balances without full page reload)
- Add/rename/remove children from admin (today: children come from journal + config sync)
- Mobile layout tweaks for narrow screens

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
- [ ] README and docs sufficient for another household to adopt without author hand-holding

## How to use this roadmap

1. **Track in git** — This file is versioned with the code; update it in the same PR as feature work when practical.
2. **Issues for tasks** — Use GitHub Issues for granular work items; keep this file for themes and phases.
3. **Defer detail** — Design notes belong in `docs/application.md` or code; avoid duplicating the full original build plan here.
