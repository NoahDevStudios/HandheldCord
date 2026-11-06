"""A thin layer over python-xlib: EWMH window management and XTEST key events.

On Wayland desktops this talks to XWayland, which is where the Discord app runs as well.
"""
from __future__ import annotations

import logging

from Xlib import X, Xatom, display, error
from Xlib.ext import xtest
from Xlib.protocol import event

log = logging.getLogger(__name__)

SOURCE_PAGER = 2  # _NET_ACTIVE_WINDOW from a pager or taskbar: window managers don't refuse it
STATE_ADD = 1
ICONIC_STATE = 3


class X11:
    """One connection to the X server."""

    def __init__(self) -> None:
        self.display = display.Display()
        self.root = self.display.screen().root
        self._atoms: dict[str, int] = {}
        # Windows can disappear between two requests; such errors are expected, not fatal.
        self.display.set_error_handler(lambda err, request: log.debug("X error ignored: %s", err))
        if not self.display.has_extension("XTEST"):
            log.error("The X server has no XTEST extension - HandheldCord can't press keys")

    def atom(self, name: str) -> int:
        if name not in self._atoms:
            self._atoms[name] = self.display.intern_atom(name)
        return self._atoms[name]

    def window(self, wid: int):
        return self.display.create_resource_object("window", wid)

    def _property(self, wid: int, name: str, kind: int = X.AnyPropertyType):
        try:
            prop = self.window(wid).get_full_property(self.atom(name), kind)
        except error.XError:
            return None
        return prop.value if prop else None

    # --- windows ----------------------------------------------------------------

    def active_window(self) -> int:
        value = self._property(self.root.id, "_NET_ACTIVE_WINDOW")
        return int(value[0]) if value is not None and len(value) else 0

    def client_windows(self) -> list[int]:
        value = self._property(self.root.id, "_NET_CLIENT_LIST")
        return [int(wid) for wid in value] if value is not None else []

    def wm_class(self, wid: int) -> str:
        """The class half of WM_CLASS in lower case, such as "discord"."""
        try:
            names = self.window(wid).get_wm_class()
        except error.XError:
            return ""
        return names[1].lower() if names else ""

    def title(self, wid: int) -> str:
        value = self._property(wid, "_NET_WM_NAME", self.atom("UTF8_STRING"))
        if value:
            return value.decode("utf-8", "replace") if isinstance(value, bytes) else str(value)
        try:
            return self.window(wid).get_wm_name() or ""
        except error.XError:
            return ""

    def pid(self, wid: int) -> int:
        value = self._property(wid, "_NET_WM_PID", Xatom.CARDINAL)
        return int(value[0]) if value is not None and len(value) else 0

    def exists(self, wid: int) -> bool:
        if not wid:
            return False
        try:
            self.window(wid).get_attributes()
        except error.XError:
            return False
        return True

    def area(self, wid: int) -> int:
        try:
            geometry = self.window(wid).get_geometry()
        except error.XError:
            return 0
        return geometry.width * geometry.height

    def _states(self, wid: int) -> set[int]:
        value = self._property(wid, "_NET_WM_STATE", Xatom.ATOM)
        return {int(atom) for atom in value} if value is not None else set()

    def is_minimized(self, wid: int) -> bool:
        return self.atom("_NET_WM_STATE_HIDDEN") in self._states(wid)

    def is_maximized(self, wid: int) -> bool:
        wanted = {self.atom("_NET_WM_STATE_MAXIMIZED_VERT"), self.atom("_NET_WM_STATE_MAXIMIZED_HORZ")}
        return wanted <= self._states(wid)

    def activate(self, wid: int) -> None:
        self._client_message(wid, "_NET_ACTIVE_WINDOW", [SOURCE_PAGER, X.CurrentTime, 0, 0, 0])

    def maximize(self, wid: int) -> None:
        vertical, horizontal = self.atom("_NET_WM_STATE_MAXIMIZED_VERT"), self.atom("_NET_WM_STATE_MAXIMIZED_HORZ")
        self._client_message(wid, "_NET_WM_STATE", [STATE_ADD, vertical, horizontal, SOURCE_PAGER, 0])

    def minimize(self, wid: int) -> None:
        self._client_message(wid, "WM_CHANGE_STATE", [ICONIC_STATE, 0, 0, 0, 0])

    def _client_message(self, wid: int, name: str, data: list[int]) -> None:
        message = event.ClientMessage(window=self.window(wid), client_type=self.atom(name), data=(32, data))
        self.root.send_event(message, event_mask=X.SubstructureRedirectMask | X.SubstructureNotifyMask)
        self.display.flush()

    # --- keys -------------------------------------------------------------------

    def keycode(self, keysym: int) -> int:
        return self.display.keysym_to_keycode(keysym)

    def keycode_and_shift(self, keysym: int) -> tuple[int, bool] | None:
        """Where the current layout has a keysym: its keycode and whether Shift is needed."""
        for keycode, index in self.display.keysym_to_keycodes(keysym):
            if index in (0, 1):
                return keycode, index == 1
        return None

    def fake_key(self, keycode: int, press: bool) -> None:
        xtest.fake_input(self.display, X.KeyPress if press else X.KeyRelease, keycode)

    def sync(self) -> None:
        self.display.sync()
