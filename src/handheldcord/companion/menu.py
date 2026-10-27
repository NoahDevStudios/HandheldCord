"""Quick menu model: quick replies, favorites, voice and app actions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class MenuItem:
    label: str
    action: str
    section: str = ""


class MenuModel:
    def __init__(self) -> None:
        self.title = ""
        self.items: list[MenuItem] = []
        self.index = 0

    def open(self, title: str, items: Iterable[MenuItem]) -> None:
        self.title = title
        self.items = list(items)
        self.index = 0

    def move(self, delta: int) -> None:
        if self.items:
            self.index = (self.index + delta) % len(self.items)

    def select(self, index: int) -> bool:
        if 0 <= index < len(self.items):
            self.index = index
            return True
        return False

    @property
    def current(self) -> MenuItem | None:
        return self.items[self.index] if self.items else None

    def snapshot(self) -> dict:
        items = []
        previous = None
        for item in self.items:
            # The first item of each section carries the section header.
            items.append({"label": item.label, "header": item.section if item.section != previous else ""})
            previous = item.section
        return {"title": self.title, "items": items, "index": self.index}
