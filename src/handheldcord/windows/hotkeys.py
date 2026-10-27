"""System-wide hotkeys via RegisterHotKey on a thread with its own message loop."""
from __future__ import annotations

import ctypes
import logging
import threading
from ctypes import wintypes
from typing import Callable

from . import win32
from .keys import hotkey_modifiers, parse_combo

log = logging.getLogger(__name__)


class GlobalHotkeys:
    """Registers hotkeys and reports presses by name.

    The callback runs on the hotkey thread; hand it over to the GUI thread
    (for example through a Qt signal) before touching any state.
    """

    def __init__(self, on_hotkey: Callable[[str], None]) -> None:
        self._on_hotkey = on_hotkey
        self._thread: threading.Thread | None = None
        self._thread_id = 0

    def start(self, hotkeys: dict[str, str]) -> None:
        self.stop()
        ready = threading.Event()
        self._thread = threading.Thread(target=self._run, args=(hotkeys, ready), name="hotkeys", daemon=True)
        self._thread.start()
        ready.wait(2.0)

    def stop(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            win32.user32.PostThreadMessageW(self._thread_id, win32.WM_QUIT, 0, 0)
            self._thread.join(2.0)
        self._thread = None

    def _run(self, hotkeys: dict[str, str], ready: threading.Event) -> None:
        self._thread_id = win32.kernel32.GetCurrentThreadId()
        msg = wintypes.MSG()
        # Create this thread's message queue before stop() can post WM_QUIT to it.
        win32.user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, win32.PM_NOREMOVE)
        names: dict[int, str] = {}
        for hotkey_id, (name, text) in enumerate(hotkeys.items(), start=1):
            if not text:
                continue
            try:
                combo = parse_combo(text)
            except ValueError as exc:
                log.warning("Hotkey %s ignored: %s", name, exc)
                continue
            if win32.user32.RegisterHotKey(None, hotkey_id, hotkey_modifiers(combo) | win32.MOD_NOREPEAT, combo.key):
                names[hotkey_id] = name
                log.info("Hotkey %s registered: %s", name, combo)
            else:
                log.warning(
                    "Hotkey %s (%s) could not be registered - is another program using it? (error %d)",
                    name, combo, ctypes.get_last_error(),
                )
        ready.set()
        try:
            while win32.user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
                if msg.message == win32.WM_HOTKEY and msg.wParam in names:
                    self._on_hotkey(names[msg.wParam])
        finally:
            for hotkey_id in names:
                win32.user32.UnregisterHotKey(None, hotkey_id)
