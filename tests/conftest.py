import pytest

from handheldcord import config
from handheldcord.companion.router import Router
from handheldcord.i18n import Translator


class FakeKeys:
    def __init__(self):
        self.calls: list[tuple[str, str]] = []

    def tap(self, combo):
        self.calls.append(("tap", combo))

    def down(self, combo):
        self.calls.append(("down", combo))

    def up(self, combo):
        self.calls.append(("up", combo))

    def type_text(self, text):
        self.calls.append(("type", text))


class FakeDiscord:
    """Window 1 is Discord, window 2 is the game."""

    def __init__(self):
        self.in_front = False
        self.running = True
        self.calls: list[str] = []

    def foreground(self):
        return 1 if self.in_front else 2

    def is_discord(self, hwnd):
        return hwnd == 1

    def find(self):
        return 1 if self.running else 0

    def show(self):
        self.calls.append("show")
        if not self.running:
            return "launching"
        self.in_front = True
        return "discord"

    def toggle(self):
        self.calls.append("toggle")
        if self.in_front:
            self.in_front = False
            return "game"
        return self.show()


class FakeUi:
    def __init__(self):
        self.context = None
        self.hints = []
        self.toasts = []
        self.osk = None
        self.menu = None
        self.wizard = None

    def context_changed(self, context, hint_list):
        self.context = context
        self.hints = hint_list

    def toast(self, text):
        self.toasts.append(text)

    def osk_changed(self, snapshot):
        self.osk = snapshot

    def menu_changed(self, snapshot):
        self.menu = snapshot

    def wizard_changed(self, snapshot):
        self.wizard = snapshot


class Harness:
    """A router with fake Win32 parts and a manual clock."""

    def __init__(self, tmp_path, **settings):
        self.cfg = config.load(tmp_path / "config.json")
        self.cfg.data.update(settings)
        self.keys = FakeKeys()
        self.discord = FakeDiscord()
        self.ui = FakeUi()
        self.now = 0.0
        self.scheduled = []
        self.router = Router(
            self.cfg, self.keys, self.discord, self.ui, Translator("en"),
            schedule=lambda delay, callback: self.scheduled.append((delay, callback)),
            clock=lambda: self.now,
        )

    def hold(self, *buttons, seconds=0.02):
        self.now += seconds
        self.router.tick(frozenset(buttons))

    def tap(self, *buttons):
        self.hold(*buttons)
        self.hold()


@pytest.fixture
def harness(tmp_path):
    return Harness(tmp_path)


@pytest.fixture
def make_harness(tmp_path):
    return lambda **settings: Harness(tmp_path, **settings)
