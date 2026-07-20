from app.api import system


def test_execute_command_uses_argument_list(monkeypatch):
    calls = []

    class Result:
        returncode = 0
        stderr = ""
        stdout = ""

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return Result()

    monkeypatch.setattr(system.subprocess, "run", fake_run)
    system.execute_command(system.SYSTEM_COMMANDS["reboot"])

    assert calls == [
        (
            ["/usr/bin/sudo", "-n", "/usr/bin/systemctl", "reboot"],
            {"capture_output": True, "text": True, "check": False},
        )
    ]


def test_routes_schedule_expected_commands(monkeypatch):
    scheduled = []
    monkeypatch.setattr(system, "run_delayed", scheduled.append)

    assert system.restart_app()["ok"]
    assert system.reboot_pi()["ok"]
    assert system.shutdown_pi()["ok"]

    assert scheduled == [
        system.SYSTEM_COMMANDS["restart-app"],
        system.SYSTEM_COMMANDS["reboot"],
        system.SYSTEM_COMMANDS["shutdown"],
    ]
