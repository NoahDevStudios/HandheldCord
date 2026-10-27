"""Sends key combos and text to whatever window is in the foreground."""
from __future__ import annotations

import logging

from . import win32
from .keys import VK_RETURN, VK_SHIFT, parse_combo

log = logging.getLogger(__name__)


class KeySender:
    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run

    def tap(self, combo: str) -> None:
        parsed = parse_combo(combo)
        events = [win32.key_event(m, False) for m in parsed.modifiers]
        events += [win32.key_event(parsed.key, False), win32.key_event(parsed.key, True)]
        events += [win32.key_event(m, True) for m in reversed(parsed.modifiers)]
        self._send(events, f"tap {combo}")

    def down(self, combo: str) -> None:
        parsed = parse_combo(combo)
        events = [win32.key_event(m, False) for m in parsed.modifiers]
        events.append(win32.key_event(parsed.key, False))
        self._send(events, f"down {combo}")

    def up(self, combo: str) -> None:
        parsed = parse_combo(combo)
        events = [win32.key_event(parsed.key, True)]
        events += [win32.key_event(m, True) for m in reversed(parsed.modifiers)]
        self._send(events, f"up {combo}")

    def type_text(self, text: str) -> None:
        events = []
        for index, line in enumerate(text.split("\n")):
            if index:
                # Enter would send the message; Discord inserts a line break on Shift+Enter.
                events += [
                    win32.key_event(VK_SHIFT, False),
                    win32.key_event(VK_RETURN, False),
                    win32.key_event(VK_RETURN, True),
                    win32.key_event(VK_SHIFT, True),
                ]
            for unit in utf16_units(line):
                events += [win32.unicode_event(unit, False), win32.unicode_event(unit, True)]
        self._send(events, f"type {len(text)} characters")

    def _send(self, events: list, description: str) -> None:
        if self.dry_run:
            log.info("[dry-run] %s", description)
            return
        log.debug("send: %s", description)
        win32.send_input(events)


def utf16_units(text: str) -> list[int]:
    """KEYEVENTF_UNICODE takes UTF-16 code units, so emoji become surrogate pairs."""
    data = text.encode("utf-16-le")
    return [int.from_bytes(data[i:i + 2], "little") for i in range(0, len(data), 2)]
