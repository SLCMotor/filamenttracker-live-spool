# Contributing

Contributions are welcome, especially hardware reports, documentation, tests,
and fixes that preserve Android and FilamentTracker Server compatibility.

## Development setup

```bash
git clone https://github.com/SLCMotor/filamenttracker-live-spool.git
cd filamenttracker-live-spool
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest
.venv/bin/ruff check software/pi-agent/app tests
```

The committed development configuration uses mock hardware, so importing or
testing the application must not require a Raspberry Pi.

Create a focused branch, include tests where practical, run the quality checks,
and explain hardware assumptions in the pull request. Do not commit calibration,
NFC dumps, local addresses, credentials, logs, or personal inventory data.

Hardware reports should include Pi model, Raspberry Pi OS/Python versions,
breakout model, backend, wiring by signal (not only wire color), and sanitized
logs. Photos must not reveal credentials, private addresses, NFC UIDs, or personal
data.

By participating, you agree to follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
For vulnerabilities, follow [SECURITY.md](SECURITY.md) instead of filing a public
issue.
