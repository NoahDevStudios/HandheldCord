"""X keysym names for HandheldCord's keys (keys.py identifies keys by Windows virtual-key codes)."""
from __future__ import annotations

from ..keys import VK_CONTROL, VK_LWIN, VK_MENU, VK_SHIFT

MODIFIER_KEYSYMS: dict[int, str] = {
    VK_CONTROL: "Control_L",
    VK_MENU: "Alt_L",
    VK_SHIFT: "Shift_L",
    VK_LWIN: "Super_L",
}

KEYSYMS: dict[int, str] = {
    0x08: "BackSpace",
    0x09: "Tab",
    0x0D: "Return",
    0x13: "Pause",
    0x1B: "Escape",
    0x20: "space",
    0x21: "Prior",
    0x22: "Next",
    0x23: "End",
    0x24: "Home",
    0x25: "Left",
    0x26: "Up",
    0x27: "Right",
    0x28: "Down",
    0x2D: "Insert",
    0x2E: "Delete",
    0x91: "Scroll_Lock",
    0xBC: "comma",
    0xBE: "period",
    **{0x6F + n: f"F{n}" for n in range(1, 25)},
    **{c: chr(c).lower() for c in range(ord("A"), ord("Z") + 1)},
    **{c: chr(c) for c in range(ord("0"), ord("9") + 1)},
}


def keysym_name(vk: int) -> str:
    return MODIFIER_KEYSYMS.get(vk) or KEYSYMS[vk]


def char_keysym(char: str) -> int:
    """Latin-1 characters are their own keysym; everything else has a Unicode keysym."""
    code = ord(char)
    return code if 0x20 <= code <= 0xFF else 0x01000000 | code
