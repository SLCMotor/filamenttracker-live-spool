from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.config import config

router = APIRouter(tags=["dashboard"])

APP_ROOT = Path(__file__).resolve().parents[2]
templates = Jinja2Templates(directory=str(APP_ROOT / "templates"))


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "app_name": config.app_name,
            "device_name": config.device_name,
            "version": config.version,
        },
    )
