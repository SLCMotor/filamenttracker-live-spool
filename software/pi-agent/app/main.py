from fastapi import FastAPI

from app.core.config import config
from app.models.status import NfcStatus, ScaleStatus, StatusResponse

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


@app.get("/status", response_model=StatusResponse)
def status():
    return StatusResponse(
        status="online",
        deviceName=config.device_name,
        version=config.version,
        scale=ScaleStatus(
            connected=False,
            stable=False,
            weightGrams=None,
        ),
        nfc=NfcStatus(
            connected=False,
            tagPresent=False,
            tagId=None,
        ),
    )
