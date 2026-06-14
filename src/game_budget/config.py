from __future__ import annotations

import os
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path

import bcrypt
import yaml

from game_budget.ledger.journal import read_journal, write_journal
from game_budget.ledger.periodic import DailyAllowanceLine, DailyBlock, replace_daily_block


@dataclass
class GamerConfig:
    name: str
    color: str = "darkgreen"
    daily_budget: Decimal = Decimal("5.00")
    savings_cron: Decimal = Decimal("0")


@dataclass
class AppConfig:
    gamers: list[GamerConfig] = field(default_factory=list)
    admin_password_hash: str = ""
    background_image: str = "/static/default-bg.svg"
    secret_key: str = ""
    allow_overdraft: bool = False

    @property
    def gamer_names(self) -> list[str]:
        return [g.name for g in self.gamers]


DEFAULT_GAMER_COLORS = {
    "Cleanrig": "darkgreen",
    "Falafel": "#0606ba",
}


def data_dir(path: Path | None = None) -> Path:
    if path is not None:
        return path
    env = os.environ.get("GAME_BUDGET_DATA")
    if env:
        return Path(env)
    return Path("data")


JOURNAL_FILENAME = "journal.dat"


def journal_path(data: Path) -> Path:
    return data / JOURNAL_FILENAME


def config_path(data: Path) -> Path:
    return data / "config.yaml"


def _parse_gamer_items(raw: dict) -> list[GamerConfig]:
    items = raw.get("gamers", raw.get("children", []))
    return [
        GamerConfig(
            name=item["name"],
            color=item.get("color", DEFAULT_GAMER_COLORS.get(item["name"], "darkgreen")),
            daily_budget=Decimal(str(item.get("daily_budget", "5.00"))),
            savings_cron=Decimal(str(item.get("savings_cron", "0"))),
        )
        for item in items
    ]


def load_config(data: Path) -> AppConfig:
    path = config_path(data)
    if not path.exists():
        return AppConfig()
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return AppConfig(
        gamers=_parse_gamer_items(raw),
        admin_password_hash=raw.get("admin_password_hash", ""),
        background_image=raw.get("background_image", "/static/default-bg.svg"),
        secret_key=raw.get("secret_key", ""),
        allow_overdraft=bool(raw.get("allow_overdraft", False)),
    )


def save_config(data: Path, config: AppConfig) -> None:
    data.mkdir(parents=True, exist_ok=True)
    payload = {
        "gamers": [
            {
                "name": gamer.name,
                "color": gamer.color,
                "daily_budget": float(gamer.daily_budget),
                "savings_cron": float(gamer.savings_cron),
            }
            for gamer in config.gamers
        ],
        "admin_password_hash": config.admin_password_hash,
        "background_image": config.background_image,
        "secret_key": config.secret_key,
        "allow_overdraft": config.allow_overdraft,
    }
    config_path(data).write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def sync_daily_block(data: Path, config: AppConfig) -> None:
    journal = journal_path(data)
    if not journal.exists():
        return
    block = DailyBlock(
        period="Daily",
        lines=tuple(
            DailyAllowanceLine(account=gamer.name, amount=gamer.daily_budget)
            for gamer in config.gamers
        ),
        balancing_account="Assets",
    )
    content = read_journal(journal)
    write_journal(journal, replace_daily_block(content, block))


def gamers_from_journal(data: Path) -> list[str]:
    journal = journal_path(data)
    if not journal.exists():
        return []
    from game_budget.ledger.periodic import split_daily_block

    _, daily, _ = split_daily_block(read_journal(journal))
    if daily is None:
        return []
    return [line.account for line in daily.lines]


def ensure_config(data: Path) -> AppConfig:
    config = load_config(data)
    if not config.secret_key:
        import secrets

        config.secret_key = secrets.token_hex(32)

    if not config.gamers:
        names = gamers_from_journal(data)
        if not names:
            names = ["Cleanrig", "Falafel"]
        config.gamers = [
            GamerConfig(
                name=name,
                color=DEFAULT_GAMER_COLORS.get(name, "darkgreen"),
            )
            for name in names
        ]

    if not config.admin_password_hash:
        config.admin_password_hash = bcrypt.hashpw(b"admin", bcrypt.gensalt()).decode()

    save_config(data, config)
    sync_daily_block(data, config)
    return config


def verify_admin_password(config: AppConfig, password: str) -> bool:
    if not config.admin_password_hash:
        return False
    return bcrypt.checkpw(password.encode(), config.admin_password_hash.encode())


def set_admin_password(config: AppConfig, password: str) -> None:
    config.admin_password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
