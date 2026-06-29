from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.services.nfc_service import get_nfc
from app.services.scale_service import scale_service


class SpoolService:
    def __init__(self) -> None:
        self.last_tag_id: str | None = None
        self.last_tag_change_at: str | None = None
        self.last_weight_grams: float | None = None
        self.last_weight_change_at: str | None = None

    def get_current_spool(self) -> dict[str, Any]:
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
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()


spool_service = SpoolService()


def get_current_spool() -> dict[str, Any]:
    return spool_service.get_current_spool()
