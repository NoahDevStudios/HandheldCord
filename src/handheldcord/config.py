"""User configuration, stored as JSON in %APPDATA%\\HandheldCord."""
from __future__ import annotations

import copy
import json
import logging
import os
from pathlib import Path

from .companion.actions import DEFAULT_BINDINGS
from .input.gestures import Timing
from .windows.keys import canonical

log = logging.getLogger(__name__)

APP_DIR = Path(os.environ.get("APPDATA") or Path.home()) / "HandheldCord"
DEFAULT_PATH = APP_DIR / "config.json"
CONFIG_VERSION = 2
MIN_REPEAT_INTERVAL_S = 0.02

DEFAULTS: dict = {
    "config_version": CONFIG_VERSION,
    "language": "auto",
    "osk_layout": "auto",
    "maximize_discord": True,
    "show_hints": True,
    # Standard keys you map to spare handheld buttons; vendor apps only offer F1-F12 and the like.
    #   overlay  HandheldCord switches between the game and Discord
    #   mute/ptt recorded as global keybinds in Discord by the setup assistant
    "handheld_keys": {"overlay": "F10", "mute": "F6", "ptt": "F7"},
    # Discord's own shortcuts, sent while Discord has the focus.
    "discord_shortcuts": {"switcher": "Ctrl+K", "emoji": "Ctrl+E", "settings": "Ctrl+,"},
    # Keybinds recorded in Discord that only HandheldCord sends, so they never need a handheld button.
    # Discord has no built-in shortcut for leaving a call, only a keybind action.
    "discord_keybinds": {"disconnect": "Ctrl+Alt+Shift+F11"},
    "quick_replies": ["gg", "brb", "1 min!", "👍"],
    "favorites": [],
    "timing": {"repeat_delay_ms": 400, "repeat_interval_ms": 80, "long_press_ms": 500, "chord_hold_ms": 500},
    "bindings": {},
    "setup_done": False,
}

# Version 1 defaults; none of them can be mapped in the handheld vendor apps.
_V1_DEFAULT_KEYS = frozenset({"F13", "F14", "F15", "Ctrl+Alt+Shift+F12"})


class Config:
    def __init__(self, path: Path, data: dict, error: str | None = None) -> None:
        self.path = path
        self.data = data
        self.error = error

    @property
    def language(self) -> str:
        return str(self.data.get("language") or "auto")

    @property
    def osk_layout(self) -> str:
        return str(self.data.get("osk_layout") or "auto")

    @property
    def maximize_discord(self) -> bool:
        return bool(self.data.get("maximize_discord", True))

    @property
    def show_hints(self) -> bool:
        return bool(self.data.get("show_hints", True))

    @property
    def handheld_keys(self) -> dict[str, str]:
        """overlay, mute and ptt; an empty string switches one off."""
        return self._combos("handheld_keys", allow_empty=True)

    def set_handheld_key(self, name: str, combo: str) -> None:
        self.data.setdefault("handheld_keys", {})[name] = canonical(combo)
        self.save()

    @property
    def discord_shortcuts(self) -> dict[str, str]:
        return self._combos("discord_shortcuts")

    @property
    def discord_keybinds(self) -> dict[str, str]:
        return self._combos("discord_keybinds")

    @property
    def quick_replies(self) -> list[str]:
        replies = self.data.get("quick_replies")
        return [r for r in replies if isinstance(r, str) and r.strip()] if isinstance(replies, list) else []

    @property
    def favorites(self) -> list[dict[str, str]]:
        """Entries like {"name": "Squad - general", "query": "general"}."""
        result = []
        for fav in self.data.get("favorites") or []:
            if isinstance(fav, dict) and isinstance(fav.get("query"), str) and fav["query"].strip():
                result.append({"name": str(fav.get("name") or fav["query"]), "query": fav["query"].strip()})
        return result

    @property
    def timing(self) -> Timing:
        raw = self.data.get("timing")
        raw = raw if isinstance(raw, dict) else {}

        def seconds(key: str) -> float:
            value = raw.get(key, DEFAULTS["timing"][key])
            if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
                value = DEFAULTS["timing"][key]
            return value / 1000.0

        return Timing(
            repeat_delay=seconds("repeat_delay_ms"),
            repeat_interval=max(MIN_REPEAT_INTERVAL_S, seconds("repeat_interval_ms")),
            long_press=seconds("long_press_ms"),
            chord_hold=seconds("chord_hold_ms"),
        )

    @property
    def bindings(self) -> dict[str, list]:
        """Default bindings; a context listed under "bindings" in the file replaces its defaults."""
        merged = copy.deepcopy(DEFAULT_BINDINGS)
        user = self.data.get("bindings")
        if isinstance(user, dict):
            for context, entries in user.items():
                if isinstance(entries, list):
                    merged[context] = entries
        return merged

    @property
    def setup_done(self) -> bool:
        return bool(self.data.get("setup_done"))

    def mark_setup_done(self) -> None:
        self.data["setup_done"] = True
        self.save()

    def save(self) -> None:
        if self.error:
            log.warning("Not saving %s because it could not be read - fix the file first", self.path)
            return
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_name(self.path.name + ".tmp")
            tmp.write_text(json.dumps(self.data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            os.replace(tmp, self.path)
        except OSError:
            log.exception("Could not save %s", self.path)

    def _combos(self, section: str, allow_empty: bool = False) -> dict[str, str]:
        defaults = DEFAULTS[section]
        raw = self.data.get(section)
        raw = raw if isinstance(raw, dict) else {}
        return {
            name: _combo(raw.get(name, default), default, f"{section}.{name}", allow_empty)
            for name, default in defaults.items()
        }


def _combo(value: object, default: str, name: str, allow_empty: bool = False) -> str:
    if allow_empty and value == "":
        return ""
    try:
        return canonical(value)
    except ValueError:
        log.warning("Invalid key combo for %s: %r - using %s", name, value, default)
        return default


def load(path: Path = DEFAULT_PATH) -> Config:
    """Read the config; on first start the defaults are written so the user can edit them."""
    data = copy.deepcopy(DEFAULTS)
    if not path.exists():
        config = Config(path, data)
        config.save()
        return config
    try:
        user = json.loads(path.read_text(encoding="utf-8-sig"))
        if not isinstance(user, dict):
            raise ValueError("the top level must be a JSON object")
    except (OSError, ValueError) as exc:
        log.error("Could not read %s: %s - using the defaults", path, exc)
        return Config(path, data, error=str(exc))
    migrated = _migrate(user)
    _merge(data, user)
    config = Config(path, data)
    if migrated:
        log.info("Updated %s to config version %d", path, CONFIG_VERSION)
        config.save()
    return config


def _migrate(user: dict) -> bool:
    """Bring a config file from an older version up to date; returns True if it changed."""
    if user.get("config_version", 1) >= CONFIG_VERSION:
        return False
    # v1 used F13-F15 and Ctrl+Alt+Shift+F12, which the handheld vendor apps cannot map.
    old_keybinds = user.pop("global_keybinds", None)
    old_keybinds = old_keybinds if isinstance(old_keybinds, dict) else {}
    old_overlay = user.pop("overlay_hotkey", None)
    keys = user.setdefault("handheld_keys", {})
    for name, value in (("overlay", old_overlay), ("mute", old_keybinds.get("mute")), ("ptt", old_keybinds.get("ptt"))):
        if isinstance(value, str) and value not in _V1_DEFAULT_KEYS:
            keys.setdefault(name, value)
    shortcuts = user.get("discord_shortcuts")
    if isinstance(shortcuts, dict):
        shortcuts.pop("mute", None)
        shortcuts.pop("deafen", None)
    # The keys changed, so Discord's keybinds have to be recorded again.
    user["setup_done"] = False
    user["config_version"] = CONFIG_VERSION
    return True


def _merge(base: dict, override: dict) -> None:
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _merge(base[key], value)
        else:
            base[key] = value
