"""Key combos such as "Ctrl+Alt+Up", shared by SendInput and RegisterHotKey."""
from __future__ import annotations

from dataclasses import dataclass

VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12  # Alt
VK_LWIN = 0x5B
VK_RETURN = 0x0D

# Canonical modifier order, used for display and for comparing combos.
_MODIFIER_ORDER = (VK_CONTROL, VK_MENU, VK_SHIFT, VK_LWIN)
_MODIFIER_NAMES = {VK_CONTROL: "Ctrl", VK_MENU: "Alt", VK_SHIFT: "Shift", VK_LWIN: "Win"}
_MODIFIER_ALIASES = {
    "CTRL": VK_CONTROL,
    "CONTROL": VK_CONTROL,
    "STRG": VK_CONTROL,
    "ALT": VK_MENU,
    "SHIFT": VK_SHIFT,
    "WIN": VK_LWIN,
}

_KEY_NAMES: dict[int, str] = {
    0x08: "Backspace",
    0x09: "Tab",
    0x0D: "Enter",
    0x1B: "Esc",
    0x20: "Space",
    0x21: "PageUp",
    0x22: "PageDown",
    0x23: "End",
    0x24: "Home",
    0x25: "Left",
    0x26: "Up",
    0x27: "Right",
    0x28: "Down",
    0x2D: "Insert",
    0x2E: "Delete",
}
_KEY_NAMES.update({0x6F + n: f"F{n}" for n in range(1, 25)})
_KEY_NAMES.update({c: chr(c) for c in range(ord("A"), ord("Z") + 1)})
_KEY_NAMES.update({c: chr(c) for c in range(ord("0"), ord("9") + 1)})

_KEY_ALIASES = {name.upper(): vk for vk, name in _KEY_NAMES.items()}
_KEY_ALIASES.update({"RETURN": 0x0D, "ESCAPE": 0x1B, "PGUP": 0x21, "PGDN": 0x22, "INS": 0x2D, "DEL": 0x2E})

# Without KEYEVENTF_EXTENDEDKEY these would arrive as numpad keys.
EXTENDED_KEYS = frozenset({0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x2D, 0x2E, VK_LWIN})

# RegisterHotKey modifier flags.
_HOTKEY_FLAGS = {VK_MENU: 0x1, VK_CONTROL: 0x2, VK_SHIFT: 0x4, VK_LWIN: 0x8}


@dataclass(frozen=True)
class Combo:
    modifiers: tuple[int, ...]
    key: int

    def __str__(self) -> str:
        key = _KEY_NAMES.get(self.key) or _MODIFIER_NAMES.get(self.key) or hex(self.key)
        return "+".join([_MODIFIER_NAMES[m] for m in self.modifiers] + [key])


def parse_combo(text: object) -> Combo:
    """Parse "Ctrl+Alt+Up" style text; raises ValueError for unknown keys."""
    parts = [part.strip().upper() for part in str(text).split("+")]
    if any(not part for part in parts):
        raise ValueError(f"invalid key combo: {text!r}")
    *names, key_name = parts
    modifiers: set[int] = set()
    for name in names:
        if name not in _MODIFIER_ALIASES:
            raise ValueError(f"unknown modifier {name!r} in {text!r}")
        modifiers.add(_MODIFIER_ALIASES[name])
    if key_name in _KEY_ALIASES:
        key = _KEY_ALIASES[key_name]
    elif key_name in _MODIFIER_ALIASES and not names:
        key = _MODIFIER_ALIASES[key_name]
    else:
        raise ValueError(f"unknown key {key_name!r} in {text!r}")
    return Combo(tuple(m for m in _MODIFIER_ORDER if m in modifiers), key)


def canonical(text: object) -> str:
    return str(parse_combo(text))


def hotkey_modifiers(combo: Combo) -> int:
    flags = 0
    for modifier in combo.modifiers:
        flags |= _HOTKEY_FLAGS[modifier]
    return flags
