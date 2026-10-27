"""Setup assistant: records Discord's global keybinds and explains the handheld buttons."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Step:
    id: str
    primary: str | None = None    # Ⓐ; None means "next step"
    secondary: str | None = None  # Ⓧ


STEPS = (
    Step("welcome"),
    Step("discord", primary="discord.show"),
    Step("mute", primary="send.mute"),
    Step("deafen", primary="send.deafen"),
    Step("ptt", primary="send.ptt"),
    Step("test", primary="send.mute", secondary="send.deafen"),
    Step("buttons"),
    Step("conflicts"),
    Step("done", primary="close"),
)


class WizardModel:
    def __init__(self) -> None:
        self.index = 0

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

    def snapshot(self, t: Callable[..., str], **params: str) -> dict:
        step = self.step
        buttons = [{
            "id": "primary",
            "glyph": "A",
            "label": t(f"wizard.{step.id}.primary", **params) if step.primary else t("wizard.next"),
        }]
        if step.secondary:
            buttons.append({"id": "secondary", "glyph": "X", "label": t(f"wizard.{step.id}.secondary", **params)})
        buttons.append({"id": "back", "glyph": "B", "label": t("wizard.back" if self.index else "wizard.close")})
        if step.primary and not self.is_last:
            buttons.append({"id": "next", "glyph": "RB", "label": t("wizard.next")})
        return {
            "step": self.index,
            "total": len(STEPS),
            "title": t(f"wizard.{step.id}.title", **params),
            "body": t(f"wizard.{step.id}.body", **params),
            "buttons": buttons,
        }
