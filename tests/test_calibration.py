from types import SimpleNamespace

from app.services import calibration_service as module


def test_calibration_is_persisted_atomically(tmp_path, monkeypatch):
    monkeypatch.setattr(module, "config", SimpleNamespace(data_dir=tmp_path))
    calibration = module.CalibrationService()
    calibration.tare(100.0)
    calibration.calibrate(raw_weight=1100.0, known_weight=1000.0)

    loaded = module.CalibrationService()
    assert loaded.calibrated
    assert loaded.zero_offset == 100.0
    assert loaded.scale_factor == 1.0
    assert loaded.calibration_file == tmp_path / "calibration.json"


def test_invalid_calibration_weight_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(module, "config", SimpleNamespace(data_dir=tmp_path))
    calibration = module.CalibrationService()
    try:
        calibration.calibrate(raw_weight=100.0, known_weight=0)
    except ValueError as error:
        assert "greater than zero" in str(error)
    else:
        raise AssertionError("Expected invalid calibration to fail")
