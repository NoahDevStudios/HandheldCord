"""Linux backend logic that needs no X server or input devices."""
import pytest

from handheldcord import keys
from handheldcord.i18n import STRINGS, Translator
from handheldcord.input.buttons import XINPUT_BITS
from handheldcord.linux import autostart
from handheldcord.linux.gamepad import _LONG_BITS, BTN_SOUTH, EV_ABS, EV_KEY, Pad, has_button
from handheldcord.linux.keymap import char_keysym, keysym_name


def test_every_key_name_has_a_keysym():
    vks = [*keys._KEY_NAMES, *keys._MODIFIER_NAMES]
    names = [keysym_name(vk) for vk in vks]
    xk = pytest.importorskip("Xlib.XK")
    assert [name for name in names if not xk.string_to_keysym(name)] == []


def test_characters_map_to_keysyms():
    assert char_keysym("g") == 0x67
    assert char_keysym("ü") == 0xFC
    assert char_keysym("👍") == 0x0101F44D


def test_pad_buttons_hat_and_axes():
    pad = Pad({0x01: (-32768, 32767), 0x02: (0, 1023)})
    pad.feed(EV_KEY, 0x130, 1)  # A
    pad.feed(EV_ABS, 0x11, -1)  # d-pad up as a hat
    pad.feed(EV_ABS, 0x01, -32768)  # left stick fully up: evdev's Y grows downwards
    pad.feed(EV_ABS, 0x02, 1023)  # left trigger with its own range
    state = pad.state()
    assert state.buttons == XINPUT_BITS["A"] | XINPUT_BITS["DPAD_UP"]
    assert state.ly == pytest.approx(1.0)
    assert state.lt == pytest.approx(1.0)
    pad.feed(EV_KEY, 0x130, 0)
    pad.feed(EV_ABS, 0x11, 0)
    assert pad.state().buttons == 0


def test_sysfs_capabilities_identify_gamepads():
    value = 1 << BTN_SOUTH
    words = []
    while value:
        words.insert(0, f"{value & ((1 << _LONG_BITS) - 1):x}")
        value >>= _LONG_BITS
    assert has_button(words, BTN_SOUTH)
    assert not has_button(["0"] * len(words), BTN_SOUTH)


def test_autostart_entry(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    monkeypatch.setattr(autostart.sys, "frozen", True, raising=False)
    monkeypatch.setattr(autostart.sys, "executable", "/home/deck/My Apps/HandheldCord/HandheldCord")
    entry = tmp_path / "autostart" / "handheldcord.desktop"
    assert autostart.apply("discord")
    assert 'Exec="/home/deck/My Apps/HandheldCord/HandheldCord" --wait-for-discord\n' in entry.read_text()
    assert autostart.apply("windows")
    assert 'Exec="/home/deck/My Apps/HandheldCord/HandheldCord"\n' in entry.read_text()
    assert autostart.apply("off")
    assert not entry.exists()


def test_desktop_entries_get_the_x11_flag_once():
    linux_discord = pytest.importorskip("handheldcord.linux.discord")
    patched = linux_discord.with_x11_flag("[Desktop Entry]\nName=Discord\nExec=/usr/bin/discord %U\n")
    assert "Exec=/usr/bin/discord %U --ozone-platform=x11\n" in patched
    assert linux_discord.with_x11_flag(patched) == patched


def test_discord_is_started_in_x11_mode(monkeypatch):
    linux_discord = pytest.importorskip("handheldcord.linux.discord")
    paths = {"discord": "/usr/bin/discord", "flatpak": "/usr/bin/flatpak"}
    monkeypatch.setattr(linux_discord.shutil, "which", paths.get)
    monkeypatch.setattr(linux_discord, "_flatpak_installed", lambda app: app == "com.discordapp.Discord")
    assert linux_discord.launch_command() == ["/usr/bin/discord", "--ozone-platform=x11"]
    flatpak = linux_discord.launch_command(prefer_flatpak=True)
    assert flatpak[:2] == ["/usr/bin/flatpak", "run"] and "--nosocket=wayland" in flatpak
    assert flatpak[-2:] == ["com.discordapp.Discord", "--ozone-platform=x11"]


def test_x11_mode_sticks_for_later_starts(monkeypatch, tmp_path):
    linux_discord = pytest.importorskip("handheldcord.linux.discord")
    home = tmp_path / "home"
    monkeypatch.setattr(linux_discord.Path, "home", classmethod(lambda cls: home))
    monkeypatch.setenv("XDG_DATA_DIRS", str(tmp_path / "usr"))
    monkeypatch.setenv("XDG_DATA_HOME", str(home / ".local/share"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(home / ".config"))
    system_entry = tmp_path / "usr" / "applications" / "discord.desktop"
    autostart_entry = home / ".config" / "autostart" / "discord.desktop"
    for entry in (system_entry, autostart_entry):
        entry.parent.mkdir(parents=True)
        entry.write_text("[Desktop Entry]\nExec=/usr/bin/discord\n", encoding="utf-8")
    linux_discord.make_x11_permanent(flatpak=False)
    user_copy = home / ".local/share/applications/discord.desktop"
    assert "Exec=/usr/bin/discord --ozone-platform=x11" in user_copy.read_text(encoding="utf-8")
    assert "Exec=/usr/bin/discord --ozone-platform=x11" in autostart_entry.read_text(encoding="utf-8")
    assert "ozone" not in system_entry.read_text(encoding="utf-8")  # system files stay untouched


def test_linux_texts_replace_the_windows_ones():
    assert Translator("en", "linux")("wizard.autostart.windows") == "At sign-in"
    assert Translator("en", "windows")("wizard.autostart.windows") == "With Windows"
    assert "Desktop Layout" in Translator("en", "linux")("wizard.conflicts.body")
    assert {key.removesuffix("@linux") for key in STRINGS["en"] if key.endswith("@linux")} <= set(STRINGS["en"])
