"""Actions understood by the companion router, and the default controller layout."""
from __future__ import annotations

from ..windows.keys import canonical

SIMPLE_ACTIONS = frozenset({
    "overlay.toggle", "app.support",
    "voice.mute", "voice.ptt", "voice.leave", "voice.disconnect",
    "discord.switcher", "discord.voice_channels", "discord.emoji", "discord.settings",
    "popup.accept", "popup.close",
    "confirm.yes", "confirm.no",
    "osk.open", "osk.close", "osk.up", "osk.down", "osk.left", "osk.right", "osk.press",
    "osk.backspace", "osk.space", "osk.shift", "osk.symbols",
    "osk.cursor_left", "osk.cursor_right", "osk.insert", "osk.send",
    "menu.open", "menu.close", "menu.up", "menu.down", "menu.select",
    "wizard.open", "wizard.close", "wizard.primary", "wizard.secondary",
    "wizard.next", "wizard.prev", "wizard.back",
    "wizard.key_prev", "wizard.key_next", "wizard.collapse", "wizard.move",
})

# "reply:0" sends quick reply 0, "favorite:0" opens favorite 0.
INDEXED_ACTIONS = ("reply", "favorite")


def normalize_action(action: object) -> str:
    """Validate an action string and bring key combos into canonical form."""
    if not isinstance(action, str) or not action:
        raise ValueError(f"invalid action: {action!r}")
    if action.startswith("key:"):
        return "key:" + canonical(action[4:])
    if action.startswith("text:"):
        return action
    prefix, colon, rest = action.partition(":")
    if colon and prefix in INDEXED_ACTIONS:
        return f"{prefix}:{int(rest)}"
    if action in SIMPLE_ACTIONS:
        return action
    raise ValueError(f"unknown action: {action!r}")


def _directions(up: str | None, down: str | None, left: str | None, right: str | None) -> list[dict]:
    """The same actions on the d-pad and the left stick, with auto-repeat."""
    bindings = []
    for direction, action in (("UP", up), ("DOWN", down), ("LEFT", left), ("RIGHT", right)):
        if action:
            bindings.append({"on": f"DPAD_{direction}", "do": action, "repeat": True})
            bindings.append({"on": f"LS_{direction}", "do": action, "repeat": True})
    return bindings


_TO_GAME = {"chord": ["VIEW", "MENU"], "do": "overlay.toggle"}

DEFAULT_BINDINGS: dict[str, list[dict]] = {
    # The game owns the controller; only the View+Menu chord is ours.
    "game": [_TO_GAME],
    "discord": [
        *_directions("key:Alt+Up", "key:Alt+Down", "key:Alt+Shift+Up", "key:Alt+Shift+Down"),
        {"on": "LB", "do": "key:Ctrl+Alt+Up", "repeat": True},
        {"on": "RB", "do": "key:Ctrl+Alt+Down", "repeat": True},
        {"on": "LT", "do": "key:PageUp", "repeat": True},
        {"on": "RT", "do": "key:PageDown", "repeat": True},
        {"on": "RS_UP", "do": "key:PageUp", "repeat": True},
        {"on": "RS_DOWN", "do": "key:PageDown", "repeat": True},
        {"on": "A", "do": "key:Enter"},
        # Alt+Up/Down skip voice channels, so holding X lists them in the quick switcher.
        {"on": "B", "tap": "key:Esc", "long": "voice.leave"},
        {"on": "X", "tap": "discord.switcher", "long": "discord.voice_channels"},
        {"on": "Y", "do": "osk.open"},
        {"on": "L3", "do": "discord.emoji"},
        {"on": "MENU", "do": "menu.open"},
        {"on": "VIEW", "do": "voice.mute"},
        _TO_GAME,
    ],
    # Discord's quick switcher or emoji picker is open.
    "discord_popup": [
        *_directions("key:Up", "key:Down", "key:Left", "key:Right"),
        {"on": "A", "do": "popup.accept"},
        {"on": "B", "do": "popup.close"},
        {"on": "X", "do": "key:Backspace", "repeat": True},
        {"on": "Y", "do": "osk.open"},
        _TO_GAME,
    ],
    "osk": [
        *_directions("osk.up", "osk.down", "osk.left", "osk.right"),
        {"on": "A", "do": "osk.press"},
        {"on": "B", "do": "osk.close"},
        {"on": "X", "do": "osk.backspace", "repeat": True},
        {"on": "Y", "do": "osk.space"},
        {"on": "LT", "do": "osk.shift"},
        {"on": "RT", "do": "osk.symbols"},
        {"on": "LB", "do": "osk.cursor_left", "repeat": True},
        {"on": "RB", "do": "osk.cursor_right", "repeat": True},
        {"on": "VIEW", "do": "osk.insert"},
        {"on": "MENU", "do": "osk.send"},
    ],
    "menu": [
        *_directions("menu.up", "menu.down", None, None),
        {"on": "A", "do": "menu.select"},
        {"on": "B", "do": "menu.close"},
        {"on": "MENU", "do": "menu.close"},
    ],
    "confirm": [
        {"on": "A", "do": "confirm.yes"},
        {"on": "B", "do": "confirm.no"},
    ],
    "wizard": [
        {"on": "A", "do": "wizard.primary"},
        {"on": "X", "do": "wizard.secondary"},
        {"on": "B", "do": "wizard.back"},
        {"on": "Y", "do": "wizard.collapse"},
        {"on": "VIEW", "do": "wizard.move"},
        {"on": "RB", "do": "wizard.next"},
        {"on": "LB", "do": "wizard.prev"},
        {"on": "DPAD_LEFT", "do": "wizard.key_prev", "repeat": True},
        {"on": "DPAD_RIGHT", "do": "wizard.key_next", "repeat": True},
        {"on": "MENU", "do": "wizard.close"},
    ],
}
