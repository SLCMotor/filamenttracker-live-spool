from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.calibration import router as calibration_router
from app.api.calibration_ui import router as calibration_ui_router
from app.api.dashboard import router as dashboard_router
from app.api.diagnostics import router as diagnostics_router
from app.api.mock import router as mock_router
from app.api.nfc import router as nfc_router
from app.api.settings_ui import router as settings_ui_router
from app.api.spool import router as spool_router
from app.api.status import router as status_router
from app.api.weight import router as weight_router
from app.core.config import config
from app.services.spool_service import start_spool_monitor, stop_spool_monitor

APP_ROOT = Path(__file__).resolve().parents[1]
STATIC_ROOT = APP_ROOT / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_spool_monitor()
    yield
    stop_spool_monitor()


app = FastAPI(
    title=config.app_name,
    version=config.version,
    description="Local Raspberry Pi API for FilamentTracker Live Spool hardware.",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=str(STATIC_ROOT)), name="static")


@app.get("/")
def root():
    return {
        "name": config.app_name,
        "version": config.version,
        "environment": config.environment,
        "status": "online",
        "message": "Live Spool API is running",
        "dashboard": "/dashboard",
        "settings": "/settings",
    }


app.include_router(dashboard_router)
app.include_router(diagnostics_router)
app.include_router(settings_ui_router)
app.include_router(status_router)
app.include_router(weight_router)
app.include_router(nfc_router)
app.include_router(spool_router)
app.include_router(calibration_router)
app.include_router(calibration_ui_router)
app.include_router(mock_router)
