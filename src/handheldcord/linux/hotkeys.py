"""System-wide hotkeys via XGrabKey on a thread with its own X connection.

On Wayland desktops the grab works while an X11 window has the focus: Discord and games running
through Proton are X11 windows. The View+Menu chord on the controller works regardless.
"""
from __future__ import annotations

import logging
import os
import select
import threading
import time
from typing import Callable

from Xlib import X, XK, display, error

from ..keys import VK_CONTROL, VK_LWIN, VK_MENU, VK_SHIFT, parse_combo
from .keymap import keysym_name

log = logging.getLogger(__name__)

_MODIFIER_MASKS = {VK_SHIFT: X.ShiftMask, VK_CONTROL: X.ControlMask, VK_MENU: X.Mod1Mask, VK_LWIN: X.Mod4Mask}
# Caps Lock and Num Lock must not break the hotkey, so it is grabbed with every combination of them.
_LOCKS = (0, X.LockMask, X.Mod2Mask, X.LockMask | X.Mod2Mask)
_IGNORED = X.LockMask | X.Mod2Mask
# X repeats a held key; presses closer together than this count as one.
REPEAT_GAP_S = 0.25


class GlobalHotkeys:
    """Registers hotkeys and reports presses by name.

    The callback runs on the hotkey thread; hand it over to the GUI thread
    (for example through a Qt signal) before touching any state.
    """

    def __init__(self, on_hotkey: Callable[[str], None]) -> None:
        self._on_hotkey = on_hotkey
        self._thread: threading.Thread | None = None
        self._wake: tuple[int, int] | None = None

    def start(self, hotkeys: dict[str, str]) -> None:
        self.stop()
        ready = threading.Event()
        self._wake = os.pipe()
        self._thread = threading.Thread(
            target=self._run, args=(hotkeys, ready, self._wake[0]), name="hotkeys", daemon=True,
        )
        self._thread.start()
        ready.wait(2.0)

    def stop(self) -> None:
        if self._thread is not None and self._thread.is_alive() and self._wake:
            os.write(self._wake[1], b"x")
            self._thread.join(2.0)
        if self._wake:
            for fd in self._wake:
                os.close(fd)
        self._thread = None
        self._wake = None

    def _run(self, hotkeys: dict[str, str], ready: threading.Event, wake: int) -> None:
        try:
            connection = display.Display()
        except Exception:
            log.exception("Hotkeys disabled: no connection to the X server")
            ready.set()
            return
        root = connection.screen().root
        grabs: dict[tuple[int, int], str] = {}
        for name, text in hotkeys.items():
            if not text:
                continue
            try:
                combo = parse_combo(text)
            except ValueError as exc:
                log.warning("Hotkey %s ignored: %s", name, exc)
                continue
            keycode = connection.keysym_to_keycode(XK.string_to_keysym(keysym_name(combo.key)))
            modifiers = 0
            for modifier in combo.modifiers:
                modifiers |= _MODIFIER_MASKS[modifier]
            refused = error.CatchError(error.BadAccess)
            for lock in _LOCKS:
                root.grab_key(keycode, modifiers | lock, True, X.GrabModeAsync, X.GrabModeAsync, onerror=refused)
            connection.sync()
            if refused.get_error():
                log.warning("Hotkey %s (%s) could not be registered - is another program using it?", name, combo)
            else:
                grabs[(keycode, modifiers)] = name
                log.info("Hotkey %s registered: %s", name, combo)
        ready.set()
        last_press: dict[str, float] = {}
        try:
            while True:
                while connection.pending_events():
                    event = connection.next_event()
                    if event.type != X.KeyPress:
                        continue
                    name = grabs.get((event.detail, event.state & 0xFF & ~_IGNORED))
                    if name is None:
                        continue
                    now = time.monotonic()
                    previous, last_press[name] = last_press.get(name, 0.0), now
                    if now - previous > REPEAT_GAP_S:
                        self._on_hotkey(name)
                readable, _, _ = select.select([connection.fileno(), wake], [], [])
                if wake in readable:
                    break
        finally:
            for keycode, modifiers in grabs:
                for lock in _LOCKS:
                    root.ungrab_key(keycode, modifiers | lock)
            connection.close()
