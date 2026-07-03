import subprocess

from fastapi import APIRouter

router = APIRouter(prefix="/system", tags=["system"])


def run_delayed(command: str) -> None:
    subprocess.Popen(
        ["bash", "-lc", f"sleep 1; {command}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


@router.post("/restart-app")
def restart_app():
    run_delayed("sudo systemctl restart live-spool-agent")
    return {"ok": True, "message": "Restarting application"}


@router.post("/reboot")
def reboot_pi():
    run_delayed("sudo systemctl reboot")
    return {"ok": True, "message": "Rebooting Raspberry Pi"}


@router.post("/shutdown")
def shutdown_pi():
    run_delayed("sudo systemctl poweroff")
    return {"ok": True, "message": "Shutting down Raspberry Pi"}
