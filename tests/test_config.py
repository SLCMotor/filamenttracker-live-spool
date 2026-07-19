from pathlib import Path

from app.core.config import Config


def write_config(path: Path) -> None:
    path.write_text(
        """
app:
  environment: production
server:
  host: 127.0.0.1
  port: 7000
hardware:
  device_mode: real
scale:
  backend: hx711
  mock: false
nfc:
  mock: false
  pn532:
    address: 0x24
""".strip()
        + "\n",
        encoding="utf-8",
    )


def test_yaml_configuration(tmp_path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    write_config(config_path)
    monkeypatch.delenv("LIVE_SPOOL_API_PORT", raising=False)
    settings = Config(config_path)
    assert settings.port == 7000
    assert settings.scale_backend == "hx711"
    assert settings.pn532_address == 0x24
    assert not settings.mock_hardware


def test_environment_overrides(tmp_path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    write_config(config_path)
    monkeypatch.setenv("LIVE_SPOOL_API_PORT", "8123")
    monkeypatch.setenv("LIVE_SPOOL_MOCK_HARDWARE", "true")
    settings = Config(config_path)
    assert settings.port == 8123
    assert settings.mock_hardware
    assert settings.scale_backend == "mock"
