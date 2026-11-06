"""Reads game controllers through the kernel's evdev interface (/dev/input/event*).

Desktop sessions give the signed-in user access to game controllers, so no root rights are needed.
Button and axis codes follow the kernel's gamepad conventions for the Xbox layout.
"""
from __future__ import annotations

import glob
import logging
import os
import struct
import time
from pathlib import Path

from ..input.buttons import XINPUT_BITS, PadState

log = logging.getLogger(__name__)

EV_KEY = 0x01
EV_ABS = 0x03
BTN_SOUTH = 0x130
RESCAN_S = 2.0
_EVENT = struct.Struct("llHHi")  # struct input_event: timeval, type, code, value
_LONG_BITS = struct.calcsize("l") * 8

BUTTONS = {
    0x130: "A",     # BTN_SOUTH
    0x131: "B",     # BTN_EAST
    0x133: "X",     # BTN_NORTH, which xpad and Steam's virtual gamepad use for X
    0x134: "Y",     # BTN_WEST
    0x136: "LB",
    0x137: "RB",
    0x13A: "VIEW",  # BTN_SELECT
    0x13B: "MENU",  # BTN_START
    0x13D: "L3",
    0x13E: "R3",
    0x220: "DPAD_UP",
    0x221: "DPAD_DOWN",
    0x222: "DPAD_LEFT",
    0x223: "DPAD_RIGHT",
}
DIGITAL_TRIGGERS = {0x138: "lt", 0x139: "rt"}  # BTN_TL2/BTN_TR2 on pads without analog triggers
STICKS = {0x00: ("lx", 1), 0x01: ("ly", -1), 0x03: ("rx", 1), 0x04: ("ry", -1)}  # evdev's Y grows downwards
TRIGGERS = {0x02: "lt", 0x05: "rt", 0x0A: "lt", 0x09: "rt"}  # ABS_Z/ABS_RZ, or ABS_BRAKE/ABS_GAS
HATS = {0x10: ("DPAD_LEFT", "DPAD_RIGHT"), 0x11: ("DPAD_UP", "DPAD_DOWN")}


class Pad:
    """The state of one controller, fed with evdev events."""

    def __init__(self, ranges: dict[int, tuple[int, int]] | None = None) -> None:
        self.ranges = ranges or {}
        self.buttons = 0
        self.axes = {"lt": 0.0, "rt": 0.0, "lx": 0.0, "ly": 0.0, "rx": 0.0, "ry": 0.0}

    def feed(self, kind: int, code: int, value: int) -> None:
        if kind == EV_KEY:
            if code in BUTTONS:
                self._set(BUTTONS[code], value != 0)
            elif code in DIGITAL_TRIGGERS:
                self.axes[DIGITAL_TRIGGERS[code]] = 1.0 if value else 0.0
        elif kind == EV_ABS:
            if code in STICKS:
                name, sign = STICKS[code]
                self.axes[name] = sign * self._scale(code, value, -1.0)
            elif code in TRIGGERS:
                self.axes[TRIGGERS[code]] = self._scale(code, value, 0.0)
            elif code in HATS:
                negative, positive = HATS[code]
                self._set(negative, value < 0)
                self._set(positive, value > 0)

    def state(self) -> PadState:
        return PadState(buttons=self.buttons, **self.axes)

    def _set(self, button: str, pressed: bool) -> None:
        bit = XINPUT_BITS[button]
        self.buttons = self.buttons | bit if pressed else self.buttons & ~bit

    def _scale(self, code: int, value: int, low: float) -> float:
        """Map the axis range onto low..1 (-1..1 for sticks, 0..1 for triggers)."""
        minimum, maximum = self.ranges.get(code, (-32768, 32767) if low < 0 else (0, 255))
        if maximum <= minimum:
            return 0.0
        result = low + (value - minimum) / (maximum - minimum) * (1.0 - low)
        return max(low, min(1.0, result))


def has_button(words: list[str], code: int) -> bool:
    """Read sysfs' capabilities/key (hex words, most significant first) for one button."""
    bits = 0
    for word in words:
        bits = (bits << _LONG_BITS) | int(word, 16)
    return bool(bits >> code & 1)


class EvdevBackend:
    def __init__(self) -> None:
        self._pads: dict[str, tuple[int, Pad]] = {}
        self._checked: dict[str, float] = {}  # device node -> ctime when it turned out not to be usable
        self._next_scan = 0.0

    @property
    def available(self) -> bool:
        return True

    def poll(self, now: float | None = None) -> list[PadState]:
        now = time.monotonic() if now is None else now
        if now >= self._next_scan:
            self._next_scan = now + RESCAN_S
            self._scan()
        states = []
        for path in list(self._pads):
            fd, pad = self._pads[path]
            if self._read(path, fd, pad):
                states.append(pad.state())
        return states

    def _scan(self) -> None:
        for path in sorted(glob.glob("/dev/input/event*")):
            if path in self._pads:
                continue
            try:
                stamp = os.stat(path).st_ctime
            except OSError:
                continue
            if self._checked.get(path) == stamp:
                continue
            self._checked[path] = stamp
            device = Path("/sys/class/input", Path(path).name, "device")
            try:
                if not has_button((device / "capabilities" / "key").read_text().split(), BTN_SOUTH):
                    continue
                name = (device / "name").read_text().strip()
            except (OSError, ValueError):
                continue
            try:
                fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
            except OSError as exc:
                log.warning("Can't read the controller %r (%s): %s", name, path, exc.strerror)
                continue
            self._pads[path] = (fd, Pad(_ranges(fd)))
            self._checked.pop(path, None)
            log.info("Controller connected: %s", name)

    def _read(self, path: str, fd: int, pad: Pad) -> bool:
        while True:
            try:
                data = os.read(fd, _EVENT.size * 64)
            except BlockingIOError:
                return True
            except OSError:
                log.info("Controller disconnected: %s", path)
                os.close(fd)
                del self._pads[path]
                return False
            if not data:
                return True
            for offset in range(0, len(data) - _EVENT.size + 1, _EVENT.size):
                _seconds, _micro, kind, code, value = _EVENT.unpack_from(data, offset)
                pad.feed(kind, code, value)


def _ranges(fd: int) -> dict[int, tuple[int, int]]:
    """Minimum and maximum of every stick and trigger axis (EVIOCGABS)."""
    import fcntl

    ranges = {}
    for code in (*STICKS, *TRIGGERS):
        info = bytearray(24)
        request = (2 << 30) | (len(info) << 16) | (ord("E") << 8) | (0x40 + code)
        try:
            fcntl.ioctl(fd, request, info)
        except OSError:
            continue
        _value, minimum, maximum = struct.unpack_from("3i", info)
        if maximum > minimum:
            ranges[code] = (minimum, maximum)
    return ranges
