from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.core.config import config

router = APIRouter(tags=["diagnostics"])

APP_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = APP_ROOT / "templates" / "diagnostics.html"


@router.get("/diagnostics", response_class=HTMLResponse)
def diagnostics():
    html = TEMPLATE_PATH.read_text(encoding="utf-8")

    html = html.replace("{{ app_name }}", config.app_name)
    html = html.replace("{{ device_name }}", config.device_name)
    html = html.replace("{{ version }}", config.version)

    return HTMLResponse(content=html)
