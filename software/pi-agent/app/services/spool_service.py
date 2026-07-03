from __future__ import annotations

import threading
import time
from datetime import datetime, timezone
from typing import Any

from app.services.nfc_service import get_nfc
from app.services.scale_service import scale_service

TAG_WEIGHT_TOLERANCE_GRAMS = 5.0


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
            "tagWeightGrams": None,
            "weightDeltaGrams": None,
            "tagWeightChanged": False,
            "weightToleranceGrams": TAG_WEIGHT_TOLERANCE_GRAMS,
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

        spool = nfc.get("tag")
        tag_weight_grams = self._number_or_none(spool.get("remainingGrams")) if isinstance(spool, dict) else None
        weight_delta_grams = None
        tag_weight_changed = False

        if tag_weight_grams is not None:
            weight_delta_grams = round(weight_grams - tag_weight_grams, 2)
            tag_weight_changed = abs(weight_delta_grams) >= TAG_WEIGHT_TOLERANCE_GRAMS

        return {
            "loaded": loaded,
            "weightGrams": weight_grams,
            "weightChanged": weight_changed,
            "lastWeightChangeAt": self.last_weight_change_at,
            "tagPresent": nfc.get("tagPresent", False),
            "tagId": tag_id,
            "tagChanged": tag_changed,
            "tagWeightGrams": tag_weight_grams,
            "weightDeltaGrams": weight_delta_grams,
            "tagWeightChanged": tag_weight_changed,
            "weightToleranceGrams": TAG_WEIGHT_TOLERANCE_GRAMS,
            "lastTagChangeAt": self.last_tag_change_at,
            "spool": spool,
            "nfc": nfc,
            "scale": scale,
            "monitorRunning": True,
            "lastUpdatedAt": self._now(),
            "error": None,
        }

    def _number_or_none(self, value: Any) -> float | None:
        if value is None or value == "":
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()


spool_service = SpoolService()


def start_spool_monitor() -> None:
    spool_service.start_monitor()


def stop_spool_monitor() -> None:
    spool_service.stop_monitor()


def get_current_spool() -> dict[str, Any]:
    return spool_service.get_current_spool()
