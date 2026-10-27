"""XInput backend: reads up to four controllers through xinput1_4.dll."""
from __future__ import annotations

import ctypes
import logging
import time
from ctypes import wintypes

from .buttons import PadState

log = logging.getLogger(__name__)

ERROR_SUCCESS = 0
MAX_PADS = 4
# XInputGetState on an empty slot is slow, so disconnected slots are probed rarely.
RECHECK_DISCONNECTED_S = 2.0


class XINPUT_GAMEPAD(ctypes.Structure):
    _fields_ = [
        ("wButtons", wintypes.WORD),
        ("bLeftTrigger", ctypes.c_ubyte),
        ("bRightTrigger", ctypes.c_ubyte),
        ("sThumbLX", ctypes.c_short),
        ("sThumbLY", ctypes.c_short),
        ("sThumbRX", ctypes.c_short),
        ("sThumbRY", ctypes.c_short),
    ]


class XINPUT_STATE(ctypes.Structure):
    _fields_ = [("dwPacketNumber", wintypes.DWORD), ("Gamepad", XINPUT_GAMEPAD)]


def _load_dll():
    loader = getattr(ctypes, "WinDLL", None)
    if loader is None:
        return None
    for name in ("xinput1_4", "xinput1_3", "xinput9_1_0"):
        try:
            dll = loader(name)
        except OSError:
            continue
        dll.XInputGetState.argtypes = [wintypes.DWORD, ctypes.POINTER(XINPUT_STATE)]
        dll.XInputGetState.restype = wintypes.DWORD
        log.debug("Using %s", name)
        return dll
    return None


def _axis(value: int) -> float:
    return max(-1.0, value / 32767.0)


class XInputBackend:
    def __init__(self) -> None:
        self._dll = _load_dll()
        if self._dll is None:
            log.error("No XInput DLL found - controller input is disabled")
        self._connected = [False] * MAX_PADS
        self._next_probe = [0.0] * MAX_PADS
        self._state = XINPUT_STATE()

    @property
    def available(self) -> bool:
        return self._dll is not None

    def poll(self, now: float | None = None) -> list[PadState]:
        if self._dll is None:
            return []
        now = time.monotonic() if now is None else now
        pads: list[PadState] = []
        for index in range(MAX_PADS):
            if not self._connected[index] and now < self._next_probe[index]:
                continue
            if self._dll.XInputGetState(index, ctypes.byref(self._state)) != ERROR_SUCCESS:
                if self._connected[index]:
                    log.info("Controller %d disconnected", index)
                self._connected[index] = False
                self._next_probe[index] = now + RECHECK_DISCONNECTED_S
                continue
            if not self._connected[index]:
                log.info("Controller %d connected", index)
                self._connected[index] = True
            pad = self._state.Gamepad
            pads.append(PadState(
                buttons=pad.wButtons,
                lt=pad.bLeftTrigger / 255.0,
                rt=pad.bRightTrigger / 255.0,
                lx=_axis(pad.sThumbLX),
                ly=_axis(pad.sThumbLY),
                rx=_axis(pad.sThumbRX),
                ry=_axis(pad.sThumbRY),
            ))
        return pads
