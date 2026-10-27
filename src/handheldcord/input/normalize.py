"""Turns raw pad snapshots into one set of pressed logical buttons."""
from __future__ import annotations

from .buttons import XINPUT_BITS, PadState


class Normalizer:
    """Merges all pads into one and converts triggers/sticks into digital buttons.

    Pads are merged with a bitwise OR, so a virtual pad from Steam Input or
    Handheld Companion that mirrors the physical one never doubles an event.
    Analog inputs use hysteresis so they don't flicker around the threshold.
    """

    def __init__(
        self,
        trigger_on: float = 0.5,
        trigger_off: float = 0.3,
        stick_on: float = 0.6,
        stick_off: float = 0.4,
    ) -> None:
        self.trigger_on = trigger_on
        self.trigger_off = trigger_off
        self.stick_on = stick_on
        self.stick_off = stick_off
        self._triggers: set[str] = set()
        self._stick_dir: dict[str, str | None] = {"LS": None, "RS": None}

    def update(self, pads: list[PadState]) -> frozenset[str]:
        bits = 0
        lt = rt = 0.0
        left = right = (0.0, 0.0)
        for pad in pads:
            bits |= pad.buttons
            lt = max(lt, pad.lt)
            rt = max(rt, pad.rt)
            if _magnitude(pad.lx, pad.ly) > _magnitude(*left):
                left = (pad.lx, pad.ly)
            if _magnitude(pad.rx, pad.ry) > _magnitude(*right):
                right = (pad.rx, pad.ry)

        pressed = {name for name, bit in XINPUT_BITS.items() if bits & bit}
        for name, value in (("LT", lt), ("RT", rt)):
            threshold = self.trigger_off if name in self._triggers else self.trigger_on
            if value >= threshold:
                self._triggers.add(name)
                pressed.add(name)
            else:
                self._triggers.discard(name)
        for prefix, (x, y) in (("LS", left), ("RS", right)):
            direction = self._stick(prefix, x, y)
            if direction:
                pressed.add(f"{prefix}_{direction}")
        return frozenset(pressed)

    def _stick(self, prefix: str, x: float, y: float) -> str | None:
        """Only the dominant axis counts, so diagonals never trigger two directions."""
        values = {"UP": y, "DOWN": -y, "RIGHT": x, "LEFT": -x}
        held = self._stick_dir[prefix]
        if held is not None and values[held] >= self.stick_off:
            return held
        best = max(values, key=values.__getitem__)
        self._stick_dir[prefix] = best if values[best] >= self.stick_on else None
        return self._stick_dir[prefix]


def _magnitude(x: float, y: float) -> float:
    return x * x + y * y
