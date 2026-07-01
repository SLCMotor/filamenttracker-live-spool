from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates

from app.core.config import config

router = APIRouter()
templates = Jinja2Templates(directory="templates")


SETTINGS_SECTIONS = {
    "general": {
        "title": "General",
        "subtitle": "Device identity and system options",
        "items": [
            ("Device Name", config.device_name),
            ("App Name", config.app_name),
            ("Version", config.version),
            ("Environment", config.environment),
        ],
    },
    "scale": {
        "title": "Scale",
        "subtitle": "Calibration and weight hardware",
        "items": [
            ("Calibration Wizard", "Available"),
            ("Tare", "Use calibration flow"),
            ("Known Weight", "250 g / 500 g / 1000 g / Custom"),
            ("Verification", "Available"),
        ],
    },
    "nfc": {
        "title": "NFC",
        "subtitle": "Tag reader and spool assignment",
        "items": [
            ("Reader", "PN532"),
            ("Tag Detection", "Available"),
            ("Tag Writing", "Planned"),
            ("Spool Assignment", "Planned"),
        ],
    },
    "display": {
        "title": "Display",
        "subtitle": "Kiosk and touchscreen behavior",
        "items": [
            ("Touchscreen", "7 inch ELECROW"),
            ("Kiosk Mode", "Enabled"),
            ("Cursor Hide", "Enabled"),
            ("Screen Blanking", "Disabled"),
        ],
    },
    "network": {
        "title": "Network",
        "subtitle": "Local API and dashboard access",
        "items": [
            ("Dashboard", "/dashboard"),
            ("Status API", "/status"),
            ("Weight API", "/weight"),
            ("Diagnostics", "/diagnostics"),
        ],
    },
    "about": {
        "title": "About",
        "subtitle": "Live Spool project information",
        "items": [
            ("Project", "FilamentTracker Live Spool"),
            ("Role", "Local sensor station"),
            ("Master App", "FilamentTracker Android"),
            ("Repository", "SLCMotor/filamenttracker-live-spool"),
        ],
    },
}


def template_context(request: Request, extra: dict | None = None):
    context = {
        "request": request,
        "app_name": config.app_name,
        "device_name": config.device_name,
        "version": config.version,
        "active_page": "settings",
    }

    if extra:
        context.update(extra)

    return context


@router.get("/settings")
def settings_page(request: Request):
    return templates.TemplateResponse(
        request,
        "settings.html",
        template_context(request, {"sections": SETTINGS_SECTIONS}),
    )


@router.get("/settings/{section_key}")
def settings_section_page(request: Request, section_key: str):
    section = SETTINGS_SECTIONS.get(section_key)

    if not section:
        raise HTTPException(status_code=404, detail="Settings section not found")

    return templates.TemplateResponse(
        request,
        "settings_section.html",
        template_context(
            request,
            {
                "section_key": section_key,
                "section": section,
            },
        ),
    )
