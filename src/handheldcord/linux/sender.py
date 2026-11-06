"""Sends key combos and text to the focused X11 window through XTEST."""
from __future__ import annotations

import logging

from Xlib import XK

from ..keys import VK_RETURN, VK_SHIFT, parse_combo
from .keymap import char_keysym, keysym_name
from .x11 import X11

log = logging.getLogger(__name__)

CLIPBOARD_RESTORE_MS = 1500


class KeySender:
    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run
        self.x = X11()
        self._keycodes: dict[int, int] = {}

    def tap(self, combo: str) -> None:
        parsed = parse_combo(combo)
        modifiers = [self._keycode(m) for m in parsed.modifiers]
        key = self._keycode(parsed.key)
        events = [(m, True) for m in modifiers] + [(key, True), (key, False)]
        events += [(m, False) for m in reversed(modifiers)]
        self._send(events, f"tap {combo}")

    def down(self, combo: str) -> None:
        parsed = parse_combo(combo)
        events = [(self._keycode(m), True) for m in parsed.modifiers] + [(self._keycode(parsed.key), True)]
        self._send(events, f"down {combo}")

    def up(self, combo: str) -> None:
        parsed = parse_combo(combo)
        events = [(self._keycode(parsed.key), False)]
        events += [(self._keycode(m), False) for m in reversed(parsed.modifiers)]
        self._send(events, f"up {combo}")

    def type_text(self, text: str) -> None:
        events = self._strokes(text)
        if events is None:
            self._paste(text)
        else:
            self._send(events, f"type {len(text)} characters")

    def _keycode(self, vk: int) -> int:
        if vk not in self._keycodes:
            self._keycodes[vk] = self.x.keycode(XK.string_to_keysym(keysym_name(vk)))
        return self._keycodes[vk]

    def _strokes(self, text: str) -> list[tuple[int, bool]] | None:
        """Key events typing the text on the current layout, or None if it lacks a character."""
        shift = self._keycode(VK_SHIFT)
        events: list[tuple[int, bool]] = []
        for char in text:
            if char == "\n":
                # Enter would send the message; Discord inserts a line break on Shift+Enter.
                enter = self._keycode(VK_RETURN)
                events += [(shift, True), (enter, True), (enter, False), (shift, False)]
                continue
            found = self.x.keycode_and_shift(char_keysym(char))
            if found is None:
                return None
            keycode, shifted = found
            if shifted:
                events.append((shift, True))
            events += [(keycode, True), (keycode, False)]
            if shifted:
                events.append((shift, False))
        return events

    def _paste(self, text: str) -> None:
        """Characters the keyboard layout lacks, such as emoji, go through the clipboard and Ctrl+V."""
        from PySide6.QtCore import QTimer
        from PySide6.QtGui import QGuiApplication

        if self.dry_run:
            log.info("[dry-run] paste %d characters", len(text))
            return
        if QGuiApplication.instance() is None:
            log.warning("Can't type %d characters: no clipboard without the app running", len(text))
            return
        clipboard = QGuiApplication.clipboard()
        previous = clipboard.text()
        clipboard.setText(text)
        self.tap("Ctrl+V")

        def restore() -> None:
            if clipboard.text() == text:
                clipboard.setText(previous)

        QTimer.singleShot(CLIPBOARD_RESTORE_MS, restore)

    def _send(self, events: list[tuple[int, bool]], description: str) -> None:
        if self.dry_run:
            log.info("[dry-run] %s", description)
            return
        log.debug("send: %s", description)
        for keycode, press in events:
            if keycode:
                self.x.fake_key(keycode, press)
        self.x.sync()
