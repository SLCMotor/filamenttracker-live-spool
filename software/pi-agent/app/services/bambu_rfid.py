from __future__ import annotations

import hashlib
import hmac
import struct
from typing import Any

try:
    from adafruit_pn532.adafruit_pn532 import MIFARE_CMD_AUTH_A
except Exception:
    MIFARE_CMD_AUTH_A = 0x60


BAMBU_RFID_HKDF_SALT = bytes(
    [
        0x9A,
        0x75,
        0x9C,
        0xF2,
        0xC4,
        0xF7,
        0xCA,
        0xFF,
        0x22,
        0x2C,
        0xB9,
        0x76,
        0x9B,
        0x41,
        0xBC,
        0x96,
    ]
)
BAMBU_RFID_HKDF_INFO = b"RFID-\x41\x00"
BAMBU_RFID_SECTOR_KEY_LENGTH = 6
BAMBU_RFID_SECTOR_KEY_COUNT = 16
BAMBU_RFID_BLOCKS_PER_SECTOR = 4


def read_bambu_rfid(pn532: Any, uid: bytes) -> dict[str, Any] | None:
    """Read and parse Bambu Lab RFID data from a MIFARE Classic tag.

    The field map intentionally mirrors the Android FilamentTracker parser so
    both products interpret Bambu tags the same way.
    """
    if not uid:
        return None

    if not hasattr(pn532, "mifare_classic_authenticate_block"):
        return {
            "isBambuTag": False,
            "uid": uid.hex().upper(),
            "rawSummary": "MIFARE Classic API not available on PN532 driver",
            "parseWarnings": ["PN532 driver does not expose MIFARE Classic raw I/O."],
        }

    blocks: dict[int, bytes] = {}
    warnings: list[str] = []
    authenticated_sectors = 0
    authenticated_sector_indexes: list[int] = []
    sector_keys = _derive_bambu_sector_keys(uid)

    for sector_index, sector_key in enumerate(sector_keys):
        sector_start_block = sector_index * BAMBU_RFID_BLOCKS_PER_SECTOR
        trailer_block = sector_start_block + BAMBU_RFID_BLOCKS_PER_SECTOR - 1

        try:
            authenticated = pn532.mifare_classic_authenticate_block(
                uid,
                sector_start_block,
                MIFARE_CMD_AUTH_A,
                sector_key,
            )
        except Exception as exc:
            warnings.append(f"Sector {sector_index} auth failed: {exc}")
            continue

        if not authenticated:
            warnings.append(f"Sector {sector_index} could not be authenticated.")
            continue

        authenticated_sectors += 1
        authenticated_sector_indexes.append(sector_index)

        for block_number in range(sector_start_block, trailer_block):
            try:
                block = pn532.mifare_classic_read_block(block_number)
            except Exception as exc:
                warnings.append(f"Block {block_number} read failed: {exc}")
                continue

            if block:
                blocks[block_number] = bytes(block)

    if not blocks:
        is_bambu_candidate = authenticated_sectors > 0
        return {
            "isBambuTag": is_bambu_candidate,
            "uid": uid.hex().upper(),
            "rawSummary": (
                "MIFARE Classic tag detected, but no Bambu data blocks were read"
                if is_bambu_candidate
                else "Tag did not authenticate with Bambu-derived MIFARE keys"
            ),
            "authenticatedSectorCount": authenticated_sectors,
            "authenticatedSectorIndexes": authenticated_sector_indexes,
            "readBlockCount": 0,
            "rawBlocks": {},
            "parseWarnings": warnings or ["No readable Bambu data blocks were captured."],
        }

    parsed = _parse_bambu_blocks(blocks)
    parsed["isBambuTag"] = True
    parsed["uid"] = uid.hex().upper()
    parsed["authenticatedSectorCount"] = authenticated_sectors
    parsed["authenticatedSectorIndexes"] = authenticated_sector_indexes
    parsed["readBlockCount"] = len(blocks)
    parsed["rawBlocks"] = _blocks_to_hex(blocks)
    parsed["rawSummary"] = (
        f"UID {uid.hex().upper()} - MIFARE Classic - "
        f"{authenticated_sectors} sectors - {len(blocks)} data blocks"
    )

    parse_warnings = list(warnings)
    if not parsed.get("material"):
        parse_warnings.append("Material was not parsed from block 2.")
    if not parsed.get("variant"):
        parse_warnings.append("Detailed material variant was not parsed from block 4.")

    parsed["parseWarnings"] = _distinct(parse_warnings)
    return parsed


def _derive_bambu_sector_keys(uid: bytes) -> list[bytes]:
    prk = hmac.new(BAMBU_RFID_HKDF_SALT, uid, hashlib.sha256).digest()
    okm = _hkdf_expand(
        pseudo_random_key=prk,
        info=BAMBU_RFID_HKDF_INFO,
        output_length=BAMBU_RFID_SECTOR_KEY_LENGTH * BAMBU_RFID_SECTOR_KEY_COUNT,
    )
    return [
        okm[index : index + BAMBU_RFID_SECTOR_KEY_LENGTH]
        for index in range(0, len(okm), BAMBU_RFID_SECTOR_KEY_LENGTH)
    ]


def _hkdf_expand(pseudo_random_key: bytes, info: bytes, output_length: int) -> bytes:
    output = bytearray()
    previous = b""
    counter = 1

    while len(output) < output_length:
        previous = hmac.new(
            pseudo_random_key,
            previous + info + bytes([counter]),
            hashlib.sha256,
        ).digest()
        output.extend(previous)
        counter += 1

    return bytes(output[:output_length])


def _parse_bambu_blocks(blocks: dict[int, bytes]) -> dict[str, Any]:
    block1 = blocks.get(1)
    block2 = blocks.get(2)
    block4 = blocks.get(4)
    block5 = blocks.get(5)
    block6 = blocks.get(6)
    block10 = blocks.get(10)
    block12 = blocks.get(12)
    block14 = blocks.get(14)

    filament_variant_id = _ascii_slice(block1, 0, 8)
    material_id = _ascii_slice(block1, 8, 16)
    material = _ascii_slice(block2, 0, 16)
    variant = _ascii_slice(block4, 0, 16)
    spool_weight_raw = _u16_le_at(block5, 4)
    spool_width_raw = _u16_le_at(block10, 4)

    return {
        "material": material,
        "variant": variant or filament_variant_id,
        "filamentCode": filament_variant_id or material_id,
        "colorHex": _rgba_hex_color(block5),
        "productionDate": _display_production_date(_ascii_slice(block12, 0, 16)),
        "hotendMinC": _u16_le_at(block6, 10),
        "hotendMaxC": _u16_le_at(block6, 8),
        "dryingTempC": _u16_le_at(block6, 0),
        "dryingHours": _u16_le_at(block6, 2),
        "spoolWeightG": _bambu_spool_weight_grams(spool_weight_raw),
        "filamentDiameterMm": _f32_le_at(block5, 8),
        "spoolWidthMm": _bambu_spool_width_mm(spool_width_raw),
        "filamentLengthM": _u16_le_at(block14, 4),
    }


def _blocks_to_hex(blocks: dict[int, bytes]) -> dict[str, str]:
    return {
        str(block_number): block.hex().upper()
        for block_number, block in sorted(blocks.items())
    }


def _ascii_slice(data: bytes | None, start: int, end_exclusive: int) -> str | None:
    if data is None or len(data) < end_exclusive:
        return None

    value = data[start:end_exclusive].decode("ascii", errors="replace")
    cleaned = value.replace("\x00", " ").strip()
    return cleaned or None


def _u16_le_at(data: bytes | None, offset: int) -> int | None:
    if data is None or len(data) < offset + 2:
        return None
    return data[offset] | (data[offset + 1] << 8)


def _f32_le_at(data: bytes | None, offset: int) -> float | None:
    if data is None or len(data) < offset + 4:
        return None
    try:
        return struct.unpack_from("<f", data, offset)[0]
    except Exception:
        return None


def _rgba_hex_color(data: bytes | None) -> str | None:
    if data is None or len(data) < 3:
        return None
    return f"#{data[0]:02X}{data[1]:02X}{data[2]:02X}"


def _bambu_spool_weight_grams(value: int | None) -> int | None:
    if value is None:
        return None
    return value * 10 if 1 <= value <= 199 else value


def _bambu_spool_width_mm(value: int | None) -> float | None:
    if value is None:
        return None
    return value / 10 if value < 1000 else value / 100


def _display_production_date(value: str | None) -> str | None:
    if not value:
        return None

    parts = value.strip().split("_")
    if len(parts) >= 5:
        return f"{parts[0]}-{parts[1]}-{parts[2]} {parts[3]}:{parts[4]}"
    return value.replace("_", " ")


def _distinct(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
