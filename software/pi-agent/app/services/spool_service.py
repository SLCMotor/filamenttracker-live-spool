from __future__ import annotations

import threading
import time
from datetime import datetime, timezone
from typing import Any

from app.services.nfc_service import get_nfc
from app.services.scale_service import scale_service


class SpoolService:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

        self.last_tag_id: str | None = None
        self.last_tag_change_at: str | None = None
        self.last_weight_grams: float | None = None
        self.last_weight_change_at: str | None = None

        self.state: dict[str, Any] = {
            "loaded": False,
            "weightGrams": 0.0,
            "weightChanged": False,
            "lastWeightChangeAt": None,
            "tagPresent": False,
            "tagId": None,
            "tagChanged": False,
            "lastTagChangeAt": None,
            "spool": None,
            "nfc": None,
            "scale": None,
            "monitorRunning": False,
            "lastUpdatedAt": None,
        }

    def start_monitor(self) -> None:
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._monitor_loop,
            name="live-spool-monitor",
            daemon=True,
        )
        self._thread.start()

    def stop_monitor(self) -> None:
        self._stop_event.set()

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)

    def get_current_spool(self) -> dict[str, Any]:
        with self._lock:
            return dict(self.state)

    def _monitor_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                new_state = self._read_current_state()

                with self._lock:
                    self.state = new_state

            except Exception as exc:
                with self._lock:
                    self.state = {
                        **self.state,
                        "monitorRunning": True,
                        "error": str(exc),
                        "lastUpdatedAt": self._now(),
                    }

            time.sleep(0.5)

    def _read_current_state(self) -> dict[str, Any]:
        scale = scale_service.get_weight()
        nfc = get_nfc()

        weight_grams = float(scale.weightGrams)
        loaded = weight_grams > 20

        tag_id = nfc.get("tagId")
        tag_changed = False

        if tag_id != self.last_tag_id:
            tag_changed = True
            self.last_tag_id = tag_id
            self.last_tag_change_at = self._now()

        weight_changed = False

        if self.last_weight_grams is None or abs(weight_grams - self.last_weight_grams) >= 5:
            weight_changed = True
            self.last_weight_grams = weight_grams
            self.last_weight_change_at = self._now()

        return {
            "loaded": loaded,
            "weightGrams": weight_grams,
            "weightChanged": weight_changed,
            "lastWeightChangeAt": self.last_weight_change_at,
            "tagPresent": nfc.get("tagPresent", False),
            "tagId": tag_id,
            "tagChanged": tag_changed,
            "lastTagChangeAt": self.last_tag_change_at,
            "spool": nfc.get("tag"),
            "nfc": nfc,
            "scale": scale,
            "monitorRunning": True,
            "lastUpdatedAt": self._now(),
            "error": None,
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()


spool_service = SpoolService()


def start_spool_monitor() -> None:
    spool_service.start_monitor()


def stop_spool_monitor() -> None:
    spool_service.stop_monitor()


def get_current_spool() -> dict[str, Any]:
    return spool_service.get_current_spool()
