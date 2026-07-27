import json

from app.services.nfc_service import NFCService


class FakePn532:
    def __init__(self, uid=b"\x04\x89\xdd\xa3\x82\x26\x81", failed_writes=None):
        self.uid = uid
        self.failed_writes = dict(failed_writes or {})
        self.pages = {}
        self.write_attempts = {}

    def read_passive_target(self, timeout=0.5):
        return self.uid

    def ntag2xx_write_block(self, page, data):
        self.write_attempts[page] = self.write_attempts.get(page, 0) + 1
        remaining = self.failed_writes.get(page, 0)
        if remaining:
            self.failed_writes[page] = remaining - 1
            return False
        self.pages[page] = bytes(data)
        return True

    def ntag2xx_read_block(self, page):
        return self.pages.get(page, b"\x00\x00\x00\x00")


def service_with(fake):
    service = NFCService.__new__(NFCService)
    service.pn532 = fake
    service.error = None
    return service


def full_server_payload():
    return {
        "app": "FT",
        "ver": 1,
        "type": "spool",
        "spoolId": "cb618005-68c7-4a69-871d-dbf585086be0",
        "filamentId": "ce0196f7-760d-496c-94b2-1be18e97bb1a",
        "brand": "SUNLU",
        "material": "Elite PETG",
        "colorName": "Digital Blue",
        "colorHex": "#1F3892",
        "initialGrams": 1000.0,
        "remainingGrams": 641.0,
        "updatedAtEpochMs": 1785188178292,
    }


def test_writes_and_verifies_full_ntag215_sized_payload():
    fake = FakePn532()
    service = service_with(fake)
    result = service._write_payload_locked(full_server_payload(), 5, None, None)

    assert result["success"] is True
    assert max(fake.pages) > 40
    assert json.loads(service._read_ntag_text()) == full_server_payload()


def test_retries_a_transient_page_write_failure():
    fake = FakePn532(failed_writes={12: 1})
    result = service_with(fake)._write_payload_locked(full_server_payload(), 5, None, None)

    assert result["success"] is True
    assert fake.write_attempts[12] == 2


def test_reports_the_exact_page_when_a_tag_rejects_the_write():
    fake = FakePn532(failed_writes={20: 3})
    result = service_with(fake)._write_payload_locked(full_server_payload(), 5, None, None)

    assert result["success"] is False
    assert result["errorCode"] == "page_write_failed"
    assert result["failedPage"] == 20
