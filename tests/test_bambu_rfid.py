import struct

from app.services.bambu_rfid import _derive_bambu_sector_keys, _parse_bambu_blocks


def test_sector_key_derivation_is_deterministic():
    keys = _derive_bambu_sector_keys(bytes.fromhex("01B76103"))
    assert len(keys) == 16
    assert all(len(key) == 6 for key in keys)
    assert keys == _derive_bambu_sector_keys(bytes.fromhex("01B76103"))


def test_bambu_block_parser_extracts_public_metadata():
    block1 = bytearray(16)
    block1[:8] = b"A00-G06 "
    block2 = bytearray(16)
    block2[:9] = b"PLA Basic"
    block5 = bytearray(16)
    block5[:4] = bytes([0, 174, 66, 255])
    block5[4:6] = (100).to_bytes(2, "little")
    struct.pack_into("<f", block5, 8, 1.75)
    parsed = _parse_bambu_blocks({1: bytes(block1), 2: bytes(block2), 5: bytes(block5)})
    assert parsed["filamentCode"] == "A00-G06"
    assert parsed["material"] == "PLA Basic"
    assert parsed["colorHex"] == "#00AE42"
    assert parsed["spoolWeightG"] == 1000
    assert round(parsed["filamentDiameterMm"], 2) == 1.75
