from fastapi import FastAPI

APP_NAME = "FilamentTracker Live Spool"
APP_VERSION = "0.1.0"

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Local Raspberry Pi API for FilamentTracker Live Spool hardware."
)


@app.get("/")
def root():
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "status": "online",
        "message": "Live Spool API is running"
    }


@app.get("/status")
def status():
    return {
        "status": "online",
        "deviceName": "Live Spool",
        "version": APP_VERSION,
        "scale": {
            "connected": False,
            "stable": False,
            "weightGrams": None
        },
        "nfc": {
            "connected": False,
            "tagPresent": False,
            "tagId": None
        }
    }
