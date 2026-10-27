"""Builds the button hint bar from whatever is bound in the active context."""
from __future__ import annotations

from typing import Callable

from ..input.gestures import ContextBindings

MAX_HINTS = 12

# Action -> i18n key. Actions without an entry don't show up in the bar.
LABELS = {
    "key:Alt+Up": "hint.channel",
    "key:Alt+Down": "hint.channel",
    "key:Alt+Shift+Up": "hint.unread",
    "key:Alt+Shift+Down": "hint.unread",
    "key:Ctrl+Alt+Up": "hint.server",
    "key:Ctrl+Alt+Down": "hint.server",
    "key:PageUp": "hint.scroll",
    "key:PageDown": "hint.scroll",
    "key:Enter": "hint.confirm",
    "key:Esc": "hint.back",
    "key:Backspace": "hint.delete",
    "discord.switcher": "hint.search",
    "discord.voice_channels": "hint.voice_channels",
    "discord.emoji": "hint.emoji",
    "discord.settings": "hint.settings",
    "osk.open": "hint.write",
    "menu.open": "hint.menu",
    "voice.mute": "hint.mute",
    "voice.ptt": "hint.ptt",
    "voice.leave": "hint.leave",
    "confirm.yes": "hint.yes",
    "confirm.no": "hint.no",
    "overlay.toggle": "hint.to_game",
    "popup.accept": "hint.select",
    "popup.close": "hint.close",
    "osk.press": "hint.key",
    "osk.close": "hint.close",
    "osk.backspace": "hint.delete",
    "osk.space": "hint.space",
    "osk.shift": "hint.shift",
    "osk.symbols": "hint.symbols",
    "osk.cursor_left": "hint.cursor",
    "osk.cursor_right": "hint.cursor",
    "osk.insert": "hint.insert",
    "osk.send": "hint.send",
    "menu.select": "hint.select",
    "menu.close": "hint.close",
}


def build(ctx: ContextBindings, t: Callable[..., str]) -> list[dict]:
    """One entry per label; buttons sharing a label are grouped ("LB/RB Server")."""
    entries: dict[str, dict] = {}

    def add(buttons: list[str], label: str, joiner: str = "/") -> None:
        entry = entries.setdefault(label, {"buttons": [], "label": label, "joiner": joiner})
        for button in buttons:
            if button not in entry["buttons"]:
                entry["buttons"].append(button)

    for button, binding in ctx.singles.items():
        if button.startswith(("LS_", "RS_")):
            continue  # the sticks mirror the d-pad and the triggers
        short = LABELS.get(binding.tap or binding.press or binding.hold or "")
        long = LABELS.get(binding.long or "")
        if short and long:
            add([button], t("hint.tap_long", tap=t(short), long=t(long)))
        elif short:
            add([button], t(short))
        elif long:
            add([button], t("hint.long", label=t(long)))
    for chord in ctx.chords:
        label = LABELS.get(chord.press or "")
        if label:
            add(list(chord.buttons), t("hint.chord", label=t(label)), joiner="+")
    return list(entries.values())[:MAX_HINTS]
