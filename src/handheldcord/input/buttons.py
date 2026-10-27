"""Logical button names shared by the whole input pipeline."""
from __future__ import annotations

from dataclasses import dataclass

# Bit flags of XINPUT_GAMEPAD.wButtons, named after the Xbox controller.
XINPUT_BITS: dict[str, int] = {
    "DPAD_UP": 0x0001,
    "DPAD_DOWN": 0x0002,
    "DPAD_LEFT": 0x0004,
    "DPAD_RIGHT": 0x0008,
    "MENU": 0x0010,
    "VIEW": 0x0020,
    "L3": 0x0040,
    "R3": 0x0080,
    "LB": 0x0100,
    "RB": 0x0200,
    "A": 0x1000,
    "B": 0x2000,
    "X": 0x4000,
    "Y": 0x8000,
}

# Digital buttons the normalizer derives from triggers and sticks.
ANALOG_BUTTONS: tuple[str, ...] = (
    "LT", "RT",
    "LS_UP", "LS_DOWN", "LS_LEFT", "LS_RIGHT",
    "RS_UP", "RS_DOWN", "RS_LEFT", "RS_RIGHT",
)

ALL_BUTTONS: frozenset[str] = frozenset(XINPUT_BITS) | frozenset(ANALOG_BUTTONS)

ALIASES: dict[str, str] = {
    "START": "MENU",
    "BACK": "VIEW",
    "SELECT": "VIEW",
}


def canonical_button(name: object) -> str:
    """Return the canonical button name, accepting a few common aliases."""
    if not isinstance(name, str):
        raise ValueError(f"invalid button: {name!r}")
    key = name.strip().upper()
    key = ALIASES.get(key, key)
    if key not in ALL_BUTTONS:
        raise ValueError(f"unknown button: {name!r}")
    return key


@dataclass(frozen=True)
class PadState:
    """One controller snapshot; sticks are -1..1, triggers 0..1."""

    buttons: int = 0
    lt: float = 0.0
    rt: float = 0.0
    lx: float = 0.0
    ly: float = 0.0
    rx: float = 0.0
    ry: float = 0.0
