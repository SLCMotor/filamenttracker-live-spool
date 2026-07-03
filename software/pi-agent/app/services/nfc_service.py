from __future__ import annotations

import json
from typing import Any, Optional

from app.services.bambu_rfid import read_bambu_rfid

try:
    import board
    import busio
    from adafruit_pn532.i2c import PN532_I2C
except Exception:
    board = None
    busio = None
    PN532_I2C = None


class NFCService:
    def __init__(self) -> None:
        self.pn532 = None
        self.error: Optional[str] = None
        self._connect()

    def _connect(self) -> None:
        if board is None or busio is None or PN532_I2C is None:
            self.error = "PN532 libraries not available"
            return

        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.pn532 = PN532_I2C(i2c, debug=False, address=0x24)
            self.pn532.SAM_configuration()
            self.error = None
        except Exception as exc:
            self.pn532 = None
            self.error = str(exc)

    def read(self) -> dict:
        if self.pn532 is None:
            self._connect()

        if self.pn532 is None:
            return self._empty_status(connected=False, error=self.error)

        try:
            uid = self.pn532.read_passive_target(timeout=0.5)

            if uid is None:
                return self._empty_status(connected=True)

            bambu_tag = self._read_bambu_rfid(uid)
            data = None if bambu_tag and bambu_tag.get("isBambuTag") else self._read_ntag_text()
            filament_tracker_tag = self._parse_filament_tracker_payload(data)

            return {
                "connected": True,
                "tagPresent": True,
                "tagId": uid.hex().upper(),
                "data": data,
                "tag": filament_tracker_tag or self._bambu_tag_summary(bambu_tag),
                "tagType": self._tag_type(filament_tracker_tag, bambu_tag),
                "bambu": bambu_tag,
                "error": None,
            }

        except Exception as exc:
            self.error = str(exc)
            self.pn532 = None
            return self._empty_status(connected=False, error=self.error)

    def erase(self) -> dict:
        if self.pn532 is None:
            self._connect()

        if self.pn532 is None:
            return {
                "success": False,
                "connected": False,
                "tagPresent": False,
                "tagId": None,
                "message": self.error or "NFC reader unavailable",
            }

        try:
            uid = self.pn532.read_passive_target(timeout=8)

            if uid is None:
                return {
                    "success": False,
                    "connected": True,
                    "tagPresent": False,
                    "tagId": None,
                    "message": "No tag detected",
                }

            tag_id = uid.hex().upper()

            # Safe logical erase for NTAG: replace user data with an empty NDEF message.
            # Avoids touching lock/configuration pages.
            self.pn532.ntag2xx_write_block(4, bytes([0x03, 0x00, 0xFE, 0x00]))

            for page in range(5, 40):
                try:
                    self.pn532.ntag2xx_write_block(page, bytes([0x00, 0x00, 0x00, 0x00]))
                except Exception:
                    break

            return {
                "success": True,
                "connected": True,
                "tagPresent": True,
                "tagId": tag_id,
                "message": "Erase successful",
            }

        except Exception as exc:
            self.error = str(exc)
            self.pn532 = None
            return {
                "success": False,
                "connected": False,
                "tagPresent": False,
                "tagId": None,
                "message": self.error,
            }

    def _empty_status(self, connected: bool, error: Optional[str] = None) -> dict:
        return {
            "connected": connected,
            "tagPresent": False,
            "tagId": None,
            "data": None,
            "tag": None,
            "tagType": None,
            "bambu": None,
            "error": error,
        }

    def _read_bambu_rfid(self, uid: bytes) -> Optional[dict[str, Any]]:
        try:
            return read_bambu_rfid(self.pn532, uid)
        except Exception as exc:
            return {
                "isBambuTag": False,
                "uid": uid.hex().upper(),
                "rawSummary": "Bambu RFID parse failed",
                "parseWarnings": [str(exc)],
            }

    def _tag_type(
        self,
        filament_tracker_tag: Optional[dict[str, Any]],
        bambu_tag: Optional[dict[str, Any]],
    ) -> Optional[str]:
        if filament_tracker_tag:
            return "filamenttracker"
        if bambu_tag and bambu_tag.get("isBambuTag"):
            return "bambu_lab_rfid"
        return None

    def _bambu_tag_summary(
        self,
        bambu_tag: Optional[dict[str, Any]],
    ) -> Optional[dict[str, Any]]:
        if not bambu_tag or not bambu_tag.get("isBambuTag"):
            return None

        return {
            "app": "Bambu Lab",
            "type": "rfid",
            "uid": bambu_tag.get("uid"),
            "brand": "Bambu Lab",
            "material": bambu_tag.get("material"),
            "variant": bambu_tag.get("variant"),
            "filamentCode": bambu_tag.get("filamentCode"),
            "colorName": bambu_tag.get("colorName"),
            "colorHex": bambu_tag.get("colorHex"),
            "hotendMinC": bambu_tag.get("hotendMinC"),
            "hotendMaxC": bambu_tag.get("hotendMaxC"),
            "dryingTempC": bambu_tag.get("dryingTempC"),
            "dryingHours": bambu_tag.get("dryingHours"),
            "spoolWeightG": bambu_tag.get("spoolWeightG"),
            "filamentDiameterMm": bambu_tag.get("filamentDiameterMm"),
            "spoolWidthMm": bambu_tag.get("spoolWidthMm"),
            "filamentLengthM": bambu_tag.get("filamentLengthM"),
            "productionDate": bambu_tag.get("productionDate"),
        }

    def _parse_filament_tracker_payload(self, data: Optional[str]) -> Optional[dict[str, Any]]:
        if not data:
            return None

        try:
            parsed = json.loads(data)

            if not isinstance(parsed, dict):
                return None

            if parsed.get("app") != "FT":
                return parsed

            return {
                "app": parsed.get("app"),
                "ver": parsed.get("ver"),
                "filamentId": parsed.get("filamentId"),
                "brand": parsed.get("brand"),
                "material": parsed.get("material"),
                "colorName": parsed.get("colorName"),
                "colorHex": parsed.get("colorHex"),
            }

        except Exception:
            return None

    def _read_ntag_text(self) -> Optional[str]:
        try:
            raw = bytearray()

            for page in range(4, 130):
                block = self.pn532.ntag2xx_read_block(page)
                if not block:
                    break

                raw.extend(block)

                if 0xFE in block:
                    break

            return self._parse_ndef(raw)

        except Exception:
            return None

    def _parse_ndef(self, raw: bytes) -> Optional[str]:
        try:
            index = 0

            while index < len(raw):
                tlv = raw[index]
                index += 1

                if tlv == 0x00:
                    continue

                if tlv == 0xFE:
                    return None

                if index >= len(raw):
                    return None

                length = raw[index]
                index += 1

                if length == 0xFF:
                    if index + 2 > len(raw):
                        return None
                    length = int.from_bytes(raw[index:index + 2], "big")
                    index += 2

                value = raw[index:index + length]
                index += length

                if tlv == 0x03:
                    return self._parse_ndef_record(value)

            return None

        except Exception:
            return None

    def _parse_ndef_record(self, record: bytes) -> Optional[str]:
        try:
            if len(record) < 4:
                return None

            header = record[0]
            short_record = bool(header & 0x10)
            type_length = record[1]

            if short_record:
                payload_length = record[2]
                record_type = record[3:3 + type_length]
                payload_start = 3 + type_length
            else:
                payload_length = int.from_bytes(record[2:6], "big")
                record_type = record[6:6 + type_length]
                payload_start = 6 + type_length

            payload = record[payload_start:payload_start + payload_length]

            if record_type == b"T" and payload:
                lang_len = payload[0] & 0x3F
                return payload[1 + lang_len:].decode("utf-8", errors="replace")

            if record_type == b"U" and payload:
                return payload[1:].decode("utf-8", errors="replace")

            if payload:
                return payload.decode("utf-8", errors="replace")

            return None

        except Exception:
            return None


nfc_service = NFCService()


def get_nfc() -> dict:
    return nfc_service.read()


def erase_nfc_tag() -> dict:
    return nfc_service.erase()
