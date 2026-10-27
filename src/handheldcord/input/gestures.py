"""Gesture detection: press with auto-repeat, tap/long press, hold and chords."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Timing:
    repeat_delay: float = 0.40
    repeat_interval: float = 0.08
    long_press: float = 0.50
    chord_hold: float = 0.50


@dataclass(frozen=True)
class Binding:
    """What one button (or a chord of buttons) does in one context.

    press  fires on press (with optional auto-repeat). If the button is part of
           a chord in the same context it fires on release instead, so the
           chord can still form.
    tap    fires on release, unless a long press or a chord used the button.
    long   fires once after Timing.long_press.
    hold   emits a "down" event on press and an "up" event on release.
    Chords only use press, which fires after Timing.chord_hold.
    """

    buttons: tuple[str, ...]
    press: str | None = None
    tap: str | None = None
    long: str | None = None
    hold: str | None = None
    repeat: bool = False

    @property
    def is_chord(self) -> bool:
        return len(self.buttons) > 1


@dataclass(frozen=True)
class Fired:
    action: str
    phase: str = "fire"  # "fire", "down" or "up"


class ContextBindings:
    def __init__(self, bindings: Iterable[Binding] = ()) -> None:
        self.singles: dict[str, Binding] = {}
        self.chords: list[Binding] = []
        for binding in bindings:
            if binding.is_chord:
                self.chords.append(binding)
            else:
                self.singles[binding.buttons[0]] = binding
        self.chord_buttons = frozenset(b for chord in self.chords for b in chord.buttons)


class GestureEngine:
    def __init__(self, timing: Timing | None = None) -> None:
        self.timing = timing or Timing()
        self._pressed: frozenset[str] = frozenset()
        self._since: dict[str, float] = {}
        self._consumed: set[str] = set()  # used up: nothing fires until released
        self._touched: set[str] = set()   # took part in a chord attempt: no tap on release
        self._repeat_at: dict[str, float] = {}
        self._holding: dict[str, str] = {}
        self._chord_since: dict[tuple[str, ...], float] = {}

    def consume_all(self) -> list[Fired]:
        """Call when the context changes: held buttons stay inert until released."""
        released = [Fired(action, "up") for action in self._holding.values()]
        self._holding.clear()
        self._consumed |= self._pressed
        self._repeat_at.clear()
        self._chord_since.clear()
        return released

    def update(self, pressed: frozenset[str], now: float, ctx: ContextBindings) -> list[Fired]:
        timing = self.timing
        fired: list[Fired] = []
        newly = pressed - self._pressed
        released = self._pressed - pressed
        for button in newly:
            self._since[button] = now

        forming: set[str] = set()
        for chord in ctx.chords:
            down = [b for b in chord.buttons if b in pressed]
            if len(down) >= 2:
                forming.update(down)
                self._touched.update(down)
            if len(down) < len(chord.buttons) or self._consumed.intersection(chord.buttons):
                self._chord_since.pop(chord.buttons, None)
                continue
            since = self._chord_since.setdefault(chord.buttons, now)
            if now - since >= timing.chord_hold:
                self._consumed.update(chord.buttons)
                self._chord_since.pop(chord.buttons, None)
                if chord.press:
                    fired.append(Fired(chord.press))

        for button in released:
            if button in self._holding:
                fired.append(Fired(self._holding.pop(button), "up"))
            binding = ctx.singles.get(button)
            if binding and button not in self._consumed and button not in self._touched:
                if binding.tap:
                    fired.append(Fired(binding.tap))
                elif binding.press and button in ctx.chord_buttons:
                    fired.append(Fired(binding.press))
            self._consumed.discard(button)
            self._touched.discard(button)
            self._repeat_at.pop(button, None)
            self._since.pop(button, None)

        for button in pressed:
            binding = ctx.singles.get(button)
            if binding is None or button in self._consumed:
                continue
            if button in newly:
                if binding.hold:
                    self._holding[button] = binding.hold
                    fired.append(Fired(binding.hold, "down"))
                if binding.press and button not in ctx.chord_buttons:
                    fired.append(Fired(binding.press))
                    if binding.repeat:
                        self._repeat_at[button] = now + timing.repeat_delay
                continue
            if binding.long and button not in forming and now - self._since.get(button, now) >= timing.long_press:
                self._consumed.add(button)
                fired.append(Fired(binding.long))
                continue
            due = self._repeat_at.get(button)
            if due is not None and now >= due and binding.press:
                fired.append(Fired(binding.press))
                self._repeat_at[button] = now + timing.repeat_interval

        self._pressed = pressed
        return fired
