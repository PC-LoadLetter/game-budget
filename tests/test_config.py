from decimal import Decimal
from pathlib import Path

import yaml

from game_budget.config import GamerConfig, load_config, save_config, AppConfig


def test_load_config_accepts_legacy_children_key(tmp_path: Path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "children": [
                    {"name": "Alice", "daily_budget": 5.0, "savings_cron": 0.0},
                ],
            }
        ),
        encoding="utf-8",
    )
    config = load_config(tmp_path)
    assert len(config.gamers) == 1
    assert config.gamers[0].name == "Alice"


def test_save_config_writes_gamers_key(tmp_path: Path):
    config = AppConfig(
        gamers=[
            GamerConfig(name="Bob", daily_budget=Decimal("7.00"), savings_cron=Decimal("1.00")),
        ],
    )
    save_config(tmp_path, config)
    raw = yaml.safe_load((tmp_path / "config.yaml").read_text(encoding="utf-8"))
    assert "gamers" in raw
    assert "children" not in raw
    assert raw["gamers"][0]["name"] == "Bob"
