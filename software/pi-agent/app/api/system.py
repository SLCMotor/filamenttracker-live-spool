import logging
import subprocess
import threading

from fastapi import APIRouter

router = APIRouter(prefix="/system", tags=["system"])
logger = logging.getLogger(__name__)

SYSTEM_COMMANDS = {
    "restart-app": [
        "/usr/bin/sudo",
        "-n",
        "/usr/bin/systemctl",
        "restart",
        "live-spool-agent",
    ],
    "reboot": ["/usr/bin/sudo", "-n", "/usr/bin/systemctl", "reboot"],
    "shutdown": ["/usr/bin/sudo", "-n", "/usr/bin/systemctl", "poweroff"],
}


def execute_command(command: list[str]) -> None:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown error"
        logger.error("System command failed (%s): %s", result.returncode, detail)


def run_delayed(command: list[str]) -> None:
    timer = threading.Timer(1.0, execute_command, args=(command,))
    timer.daemon = True
    timer.start()


@router.post("/restart-app")
def restart_app():
    run_delayed(SYSTEM_COMMANDS["restart-app"])
    return {"ok": True, "message": "Restarting application"}


@router.post("/reboot")
def reboot_pi():
    run_delayed(SYSTEM_COMMANDS["reboot"])
    return {"ok": True, "message": "Rebooting Raspberry Pi"}


@router.post("/shutdown")
def shutdown_pi():
    run_delayed(SYSTEM_COMMANDS["shutdown"])
    return {"ok": True, "message": "Shutting down Raspberry Pi"}
