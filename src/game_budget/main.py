from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from game_budget.config import FIXTURE_JOURNAL_FILENAME, data_dir, ensure_config, load_config
from game_budget.service import init_data, maybe_run_savings_cron
from game_budget.web.routes_admin import router as admin_router
from game_budget.web.routes_kiosk import router as kiosk_router

PACKAGE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = PACKAGE_DIR / "web" / "templates"
STATIC_DIR = PACKAGE_DIR / "web" / "static"


def create_app(data: Path | None = None) -> FastAPI:
    data_path = data_dir(data)
    sample = Path(__file__).resolve().parents[2] / "samples" / FIXTURE_JOURNAL_FILENAME
    init_data(data_path, sample_journal=sample if sample.exists() else None)
    config = ensure_config(data_path)
    maybe_run_savings_cron(data_path, config)

    app = FastAPI(title="Game Budget")
    app.state.data_dir = data_path
    app.state.templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.middleware("http")
    async def refresh_config(request: Request, call_next):
        request.state.config = load_config(app.state.data_dir)
        response = await call_next(request)
        return response

    app.include_router(kiosk_router)
    app.include_router(admin_router)
    return app
