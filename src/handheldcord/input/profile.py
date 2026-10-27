"""Parses binding definitions (as stored in config.json) into ContextBindings."""
from __future__ import annotations

import logging
from typing import Callable

from .buttons import canonical_button
from .gestures import Binding, ContextBindings

log = logging.getLogger(__name__)

ActionNormalizer = Callable[[object], str]


def parse_binding(raw: object, normalize: ActionNormalizer) -> Binding:
    """Parse one entry such as {"on": "A", "do": "key:Enter"}.

    Raises ValueError or TypeError for invalid entries.
    """
    if not isinstance(raw, dict):
        raise ValueError("a binding must be a JSON object")
    if "chord" in raw:
        buttons = tuple(dict.fromkeys(canonical_button(b) for b in raw["chord"]))
        if len(buttons) < 2:
            raise ValueError("a chord needs at least two different buttons")
    elif "on" in raw:
        buttons = (canonical_button(raw["on"]),)
    else:
        raise ValueError('a binding needs "on" or "chord"')

    actions = {key: normalize(raw[key]) for key in ("do", "tap", "long", "hold") if raw.get(key)}
    if not actions:
        raise ValueError("the binding has no action")
    press, tap = actions.get("do"), actions.get("tap")
    if press and "long" in actions and not tap:
        # With a long press on the same button, "do" can only fire on release.
        press, tap = None, press
    if len(buttons) > 1 and (not press or len(actions) > 1):
        raise ValueError('chords only support "do"')
    return Binding(
        buttons=buttons,
        press=press,
        tap=tap,
        long=actions.get("long"),
        hold=actions.get("hold"),
        repeat=bool(raw.get("repeat", False)),
    )


def load_profile(contexts: dict, normalize: ActionNormalizer) -> dict[str, ContextBindings]:
    """Parse all contexts; invalid entries are logged and skipped."""
    profile: dict[str, ContextBindings] = {}
    for name, entries in contexts.items():
        bindings = []
        for raw in entries if isinstance(entries, list) else []:
            try:
                bindings.append(parse_binding(raw, normalize))
            except (ValueError, TypeError) as exc:
                log.warning("Ignoring binding %r in context %r: %s", raw, name, exc)
        profile[name] = ContextBindings(bindings)
    return profile
