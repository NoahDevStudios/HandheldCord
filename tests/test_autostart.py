import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path

from handheldcord.windows import autostart, win32


class FakeRegistry:
    """Just enough of winreg for the Run key."""

    HKEY_CURRENT_USER = "HKCU"
    KEY_SET_VALUE = 2
    REG_SZ = 1

    def __init__(self):
        self.values = {}

    @contextmanager
    def OpenKey(self, root, path, reserved, access):
        assert (root, path) == ("HKCU", autostart.RUN_KEY)
        yield path

    def SetValueEx(self, key, name, reserved, kind, value):
        self.values[name] = value

    def DeleteValue(self, key, name):
        if name not in self.values:
            raise FileNotFoundError(name)
        del self.values[name]


def test_autostart_writes_and_removes_the_run_entry(monkeypatch):
    registry = FakeRegistry()
    monkeypatch.setattr(autostart, "winreg", registry)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", r"C:\Games\Handheld Cord\HandheldCord.exe")
    assert autostart.apply("discord")
    assert registry.values == {"HandheldCord": r'"C:\Games\Handheld Cord\HandheldCord.exe" --wait-for-discord'}
    autostart.apply("windows")
    assert registry.values == {"HandheldCord": r'"C:\Games\Handheld Cord\HandheldCord.exe"'}
    assert autostart.apply("off")
    assert registry.values == {}
    assert autostart.apply("off")  # nothing left to remove is fine


def test_autostart_from_source_uses_the_windowless_interpreter(monkeypatch, tmp_path):
    (tmp_path / "pythonw.exe").write_text("")
    monkeypatch.delattr(sys, "frozen", raising=False)
    monkeypatch.setattr(sys, "executable", str(tmp_path / "python.exe"))
    expected = subprocess.list2cmdline([str(tmp_path / "pythonw.exe"), "-m", "handheldcord"])
    assert autostart.command("windows") == expected


def test_running_processes_are_listed():
    assert Path(sys.executable).name.lower() in win32.process_names()
