from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from game_budget.auth import (
    SESSION_COOKIE,
    create_admin_session,
    generate_csrf_token,
    validate_admin_session,
    validate_csrf_token,
)
from game_budget.config import (
    ChildConfig,
    ensure_config,
    journal_path,
    save_config,
    set_admin_password,
    sync_daily_block,
    verify_admin_password,
)

router = APIRouter(prefix="/admin")


def _require_admin(request: Request) -> bool:
    token = request.cookies.get(SESSION_COOKIE)
    return validate_admin_session(request.state.config, token)


@router.get("", response_class=HTMLResponse)
async def admin_home(request: Request):
    if not _require_admin(request):
        return request.app.state.templates.TemplateResponse(
            request,
            "admin/login.html",
            {"csrf_token": generate_csrf_token(request.state.config), "error": None},
        )
    config = request.state.config
    return request.app.state.templates.TemplateResponse(
        request,
        "admin/index.html",
        {
            "config": config,
            "csrf_token": generate_csrf_token(config),
        },
    )


@router.post("/login")
async def admin_login(request: Request):
    form = await request.form()
    config = request.state.config
    csrf_token = str(form.get("csrf_token", ""))
    password = str(form.get("password", ""))
    if not validate_csrf_token(config, csrf_token):
        return request.app.state.templates.TemplateResponse(
            request,
            "admin/login.html",
            {"csrf_token": generate_csrf_token(config), "error": "Invalid form token."},
            status_code=400,
        )
    if not verify_admin_password(config, password):
        return request.app.state.templates.TemplateResponse(
            request,
            "admin/login.html",
            {"csrf_token": generate_csrf_token(config), "error": "Wrong password."},
            status_code=401,
        )
    response = RedirectResponse("/admin", status_code=303)
    response.set_cookie(SESSION_COOKIE, create_admin_session(config), httponly=True, samesite="lax")
    return response


@router.post("/settings")
async def admin_settings(request: Request):
    if not _require_admin(request):
        return RedirectResponse("/admin", status_code=303)
    config = request.state.config
    data = request.app.state.data_dir
    form = await request.form()
    if not validate_csrf_token(config, str(form.get("csrf_token", ""))):
        return RedirectResponse("/admin", status_code=303)

    updated: list[ChildConfig] = []
    for child in config.children:
        daily = form.get(f"daily_{child.name}", child.daily_budget)
        savings = form.get(f"savings_{child.name}", child.savings_cron)
        updated.append(
            ChildConfig(
                name=child.name,
                color=child.color,
                daily_budget=Decimal(str(daily)),
                savings_cron=Decimal(str(savings)),
            )
        )
    config.children = updated
    config.allow_overdraft = form.get("allow_overdraft") == "on"
    config.background_image = str(form.get("background_image", config.background_image))
    save_config(data, config)
    sync_daily_block(data, config)
    return RedirectResponse("/admin", status_code=303)


@router.post("/password")
async def admin_password(request: Request):
    if not _require_admin(request):
        return RedirectResponse("/admin", status_code=303)
    config = request.state.config
    data = request.app.state.data_dir
    form = await request.form()
    if validate_csrf_token(config, str(form.get("csrf_token", ""))):
        new_password = str(form.get("new_password", ""))
        if new_password:
            set_admin_password(config, new_password)
            save_config(data, config)
    return RedirectResponse("/admin", status_code=303)


@router.get("/export")
async def admin_export(request: Request):
    if not _require_admin(request):
        return RedirectResponse("/admin", status_code=303)
    journal = journal_path(request.app.state.data_dir)
    return FileResponse(journal, filename="boys.dat", media_type="text/plain")


@router.post("/import")
async def admin_import(
    request: Request,
    csrf_token: str = Form(""),
    journal_file: UploadFile = File(...),
):
    if not _require_admin(request):
        return RedirectResponse("/admin", status_code=303)
    config = request.state.config
    data = request.app.state.data_dir
    if not validate_csrf_token(config, csrf_token):
        return RedirectResponse("/admin", status_code=303)

    import shutil

    journal = journal_path(data)
    if journal.exists():
        shutil.copy(journal, journal.with_suffix(".dat.bak"))
    journal.write_bytes(await journal_file.read())
    ensure_config(data)
    return RedirectResponse("/admin", status_code=303)
