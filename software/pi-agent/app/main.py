from fastapi import FastAPI

from app.api.mock import router as mock_router
from app.api.status import router as status_router
from app.api.weight import router as weight_router
from app.core.config import config

app = FastAPI(
    title=config.app_name,
    version=config.version,
    description="Local Raspberry Pi API for FilamentTracker Live Spool hardware.",
)


@app.get("/")
def root():
    return {
        "name": config.app_name,
        "version": config.version,
        "environment": config.environment,
        "status": "online",
        "message": "Live Spool API is running",
    }


app.include_router(status_router)
app.include_router(weight_router)
app.include_router(mock_router)
