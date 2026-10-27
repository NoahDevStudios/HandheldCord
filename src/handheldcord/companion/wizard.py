"""Setup assistant: picks the handheld keys and records them as Discord keybinds."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

# Vendor apps (Armoury Crate SE, Legion Space, MSI Center M) map buttons to F1-F12, not to F13 and up.
KEY_CHOICES = tuple(f"F{n}" for n in range(1, 13))
POSITIONS = ("bottom-right", "bottom-left", "top-right", "top-left")


@dataclass(frozen=True)
class Step:
    id: str
    primary: str | None = None    # Ⓐ; None means "next step"
    secondary: str | None = None  # Ⓧ
    key: str | None = None        # handheld key chosen with ◀ ▶ on this step
    record: str | None = None     # key that Ⓐ sends to Discord's "Record Keybind" field


STEPS = (
    Step("welcome"),
    Step("discord", primary="discord.show"),
    Step("overlay", key="overlay"),
    Step("mute", primary="record", secondary="discord.settings", key="mute", record="mute"),
    Step("ptt", primary="record", secondary="discord.settings", key="ptt", record="ptt"),
    Step("leave", primary="record", secondary="discord.settings", record="leave"),
    Step("test", primary="test.mute"),
    Step("buttons"),
    Step("conflicts"),
    Step("done", primary="close"),
)


class WizardModel:
    def __init__(self) -> None:
        self.index = 0
        self.collapsed = False
        self.position = 0

    @property
    def step(self) -> Step:
        return STEPS[self.index]

    @property
    def is_last(self) -> bool:
        return self.index == len(STEPS) - 1

    def next(self) -> bool:
        if self.is_last:
            return False
        self.index += 1
        return True

    def prev(self) -> bool:
        if self.index == 0:
            return False
        self.index -= 1
        return True

    def toggle_collapsed(self) -> None:
        self.collapsed = not self.collapsed

    def move(self) -> None:
        """Dock in the next corner, so whatever Discord shows behind it can be read."""
        self.position = (self.position + 1) % len(POSITIONS)

    def snapshot(self, t: Callable[..., str], keys: dict[str, str], **params: str) -> dict:
        step = self.step
        params = {**keys, **params}
        key = keys.get(step.key, "") if step.key else ""
        if step.primary == "record":
            primary = t("wizard.record", key=keys.get(step.record or "", ""))
        elif step.primary:
            primary = t(f"wizard.{step.id}.primary", **params)
        else:
            primary = t("wizard.next")
        buttons = [{"id": "primary", "glyph": "A", "label": primary}]
        if step.secondary:
            buttons.append({"id": "secondary", "glyph": "X", "label": t("wizard.open_settings")})
        buttons.append({"id": "back", "glyph": "B", "label": t("wizard.back" if self.index else "wizard.close")})
        if step.primary and not self.is_last:
            buttons.append({"id": "next", "glyph": "RB", "label": t("wizard.next")})
        return {
            "step": self.index,
            "total": len(STEPS),
            "title": t(f"wizard.{step.id}.title", **params),
            "body": t(f"wizard.{step.id}.body", **params),
            "buttons": buttons,
            "key": {"caption": t("wizard.key"), "label": key or "–"} if step.key else None,
            "controls": [
                {"id": "collapse", "glyph": "Y", "label": t("wizard.collapse")},
                {"id": "move", "glyph": "VIEW", "label": t("wizard.move")},
            ],
            "collapsed": self.collapsed,
            "expandLabel": t("wizard.expand"),
            "position": POSITIONS[self.position],
        }
