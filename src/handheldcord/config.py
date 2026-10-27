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
MIN_REPEAT_INTERVAL_S = 0.02

DEFAULTS: dict = {
    "language": "auto",
    "osk_layout": "auto",
    "maximize_discord": True,
    "show_hints": True,
    # A spare handheld button mapped to this combo switches between game and Discord.
    "overlay_hotkey": "Ctrl+Alt+Shift+F12",
    # Recorded as global keybinds in Discord by the setup assistant; they work in games.
    "global_keybinds": {"mute": "F13", "deafen": "F14", "ptt": "F15"},
    # Discord's own shortcuts, used while Discord has the focus.
    "discord_shortcuts": {"mute": "Ctrl+Shift+M", "deafen": "Ctrl+Shift+D", "switcher": "Ctrl+K", "emoji": "Ctrl+E"},
    "quick_replies": ["gg", "brb", "1 min!", "👍"],
    "favorites": [],
    "timing": {"repeat_delay_ms": 400, "repeat_interval_ms": 80, "long_press_ms": 500, "chord_hold_ms": 500},
    "bindings": {},
    "setup_done": False,
}


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
    def overlay_hotkey(self) -> str:
        """An empty string disables the hotkey."""
        return _combo(self.data.get("overlay_hotkey"), DEFAULTS["overlay_hotkey"], "overlay_hotkey", allow_empty=True)

    @property
    def global_keybinds(self) -> dict[str, str]:
        return self._combos("global_keybinds")

    @property
    def discord_shortcuts(self) -> dict[str, str]:
        return self._combos("discord_shortcuts")

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

    def _combos(self, section: str) -> dict[str, str]:
        defaults = DEFAULTS[section]
        raw = self.data.get(section)
        raw = raw if isinstance(raw, dict) else {}
        return {name: _combo(raw.get(name, default), default, f"{section}.{name}") for name, default in defaults.items()}


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
    _merge(data, user)
    return Config(path, data)


def _merge(base: dict, override: dict) -> None:
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _merge(base[key], value)
        else:
            base[key] = value
