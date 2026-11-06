"""The Linux backends against a real X server (CI runs Xvfb with Openbox) and a virtual gamepad."""
import os
import struct
import subprocess
import sys
import time
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    not sys.platform.startswith("linux") or not os.environ.get("DISPLAY"), reason="needs an X server",
)
pytest.importorskip("Xlib")

from Xlib import X, XK, display  # noqa: E402


def wait_until(condition, timeout=5.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(0.05)
    return condition()


@pytest.fixture
def discord_window():
    """A window that looks like Discord's: WM_CLASS "discord" and a title."""
    connection = display.Display()
    screen = connection.screen()
    window = screen.root.create_window(
        20, 20, 500, 300, 0, screen.root_depth, X.InputOutput, X.CopyFromParent,
        background_pixel=screen.white_pixel, event_mask=X.KeyPressMask | X.KeyReleaseMask,
    )
    window.set_wm_class("discord", "discord")
    window.set_wm_name("Discord")
    window.change_property(connection.intern_atom("_NET_WM_NAME"), connection.intern_atom("UTF8_STRING"), 8,
                           b"#general - Discord")
    window.map()
    connection.sync()
    yield connection, window
    window.destroy()
    connection.close()


def focused_discord(window):
    from handheldcord.linux.discord import DiscordWindows

    discord = DiscordWindows(maximize=False)
    assert wait_until(lambda: discord.find() == window.id)
    assert discord.show() == "discord"
    assert wait_until(lambda: discord.foreground() == window.id)
    return discord


def key_presses(connection, window, seconds=1.5):
    """(keysym, state) of the non-modifier key presses the window received."""
    modifiers = {XK.string_to_keysym(name) for name in ("Control_L", "Shift_L", "Alt_L", "Super_L")}
    presses = []
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        while connection.pending_events():
            event = connection.next_event()
            if event.type == X.KeyPress and event.window.id == window.id:
                keysym = connection.keycode_to_keysym(event.detail, 1 if event.state & X.ShiftMask else 0)
                if keysym not in modifiers:
                    presses.append((keysym, event.state))
        time.sleep(0.02)
    return presses


def test_discord_window_is_found_focused_and_left(discord_window):
    _, window = discord_window
    discord = focused_discord(window)
    assert discord.is_discord(window.id)
    discord.back()  # nothing was in front before, so Discord gets minimized
    assert wait_until(lambda: discord.x.is_minimized(window.id))


def test_keys_and_text_reach_discord(discord_window):
    from handheldcord.linux.sender import KeySender

    connection, window = discord_window
    focused_discord(window)
    sender = KeySender()
    sender.tap("Ctrl+K")
    sender.type_text("g!")
    presses = key_presses(connection, window)
    assert [keysym for keysym, _ in presses] == [XK.string_to_keysym(name) for name in ("k", "g", "exclam")]
    assert presses[0][1] & X.ControlMask
    assert presses[2][1] & X.ShiftMask


def test_overlay_hotkey_fires():
    from handheldcord.linux.hotkeys import GlobalHotkeys
    from handheldcord.linux.sender import KeySender

    fired = []
    hotkeys = GlobalHotkeys(fired.append)
    hotkeys.start({"overlay": "F10"})
    try:
        KeySender().tap("F10")
        assert wait_until(lambda: fired == ["overlay"])
    finally:
        hotkeys.stop()


def test_app_starts_on_x11(tmp_path):
    config = tmp_path / "config.json"
    config.write_text('{"setup_done": true}', encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "handheldcord", "--dry-run", "--config", str(config), "--exit-after", "3"],
        capture_output=True, text=True, timeout=60,
    )
    log = (tmp_path / "handheldcord.log").read_text(encoding="utf-8")
    assert result.returncode == 0, result.stderr
    assert "starting" in log and "Hotkey overlay registered: F10" in log
    assert "Could not load" not in log and "Traceback" not in log


UINPUT = Path("/dev/uinput")


@pytest.mark.skipif(not os.access(UINPUT, os.W_OK), reason="no writable /dev/uinput")
def test_virtual_gamepad_is_read():
    """A uinput gamepad shows up in the backend and its A button is seen."""
    import fcntl

    from handheldcord.input.buttons import XINPUT_BITS
    from handheldcord.linux.gamepad import EvdevBackend

    def ioctl_int(fd, number, value):
        fcntl.ioctl(fd, (1 << 30) | (4 << 16) | (ord("U") << 8) | number, value)

    def emit(fd, kind, code, value):
        os.write(fd, struct.pack("llHHi", 0, 0, kind, code, value))

    fd = os.open(UINPUT, os.O_WRONLY | os.O_NONBLOCK)
    try:
        ioctl_int(fd, 100, 0x01)  # UI_SET_EVBIT: EV_KEY
        for code in (0x130, 0x131, 0x133, 0x134, 0x13A, 0x13B):
            ioctl_int(fd, 101, code)  # UI_SET_KEYBIT
        # struct uinput_user_dev: name, input_id, ff_effects_max, absmax/absmin/absfuzz/absflat[64]
        os.write(fd, struct.pack("80sHHHHi", b"HandheldCord test pad", 0x03, 0x045E, 0x028E, 1, 0) + bytes(4 * 64 * 4))
        fcntl.ioctl(fd, (ord("U") << 8) | 1)  # UI_DEV_CREATE
        backend = EvdevBackend()
        now = [0.0]

        def pads():
            now[0] += 10
            return backend.poll(now[0])

        assert wait_until(lambda: len(pads()) == 1)
        emit(fd, 0x01, 0x130, 1)
        emit(fd, 0x00, 0, 0)  # SYN_REPORT
        assert wait_until(lambda: pads()[0].buttons & XINPUT_BITS["A"])
    finally:
        fcntl.ioctl(fd, (ord("U") << 8) | 2)  # UI_DEV_DESTROY
        os.close(fd)
