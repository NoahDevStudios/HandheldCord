"""Companion-mode router: turns controller gestures into Discord shortcuts and overlay actions."""
from __future__ import annotations

import logging
import time
from typing import Callable, Protocol

from .. import SUPPORT_URL, __author__, __version__
from ..config import AUTOSTART_MODES
from ..input.gestures import ContextBindings, Fired, GestureEngine
from ..input.profile import load_profile
from . import hints
from .actions import normalize_action
from .menu import MenuItem, MenuModel
from .osk import LETTER_ROWS, OskModel
from .wizard import KEY_CHOICES, WizardModel

log = logging.getLogger(__name__)

# Layers that only make sense on top of Discord; they close when it loses the foreground.
DISCORD_LAYERS = ("osk", "menu", "confirm", "discord_popup")
LAUNCH_TIMEOUT_S = 30.0
SWITCHER_TYPE_DELAY_S = 0.15
SWITCHER_ENTER_DELAY_S = 0.6
SETTINGS_DELAY_S = 0.3
_EMPTY = ContextBindings()


class Keys(Protocol):
    def tap(self, combo: str) -> None: ...
    def down(self, combo: str) -> None: ...
    def up(self, combo: str) -> None: ...
    def type_text(self, text: str) -> None: ...


class Discord(Protocol):
    def foreground(self) -> int: ...
    def is_discord(self, hwnd: int) -> bool: ...
    def find(self) -> int: ...
    def show(self) -> str: ...
    def toggle(self) -> str: ...


class Ui(Protocol):
    def context_changed(self, context: str, hint_list: list[dict]) -> None: ...
    def toast(self, text: str) -> None: ...
    def osk_changed(self, snapshot: dict | None) -> None: ...
    def menu_changed(self, snapshot: dict | None) -> None: ...
    def confirm_changed(self, snapshot: dict | None) -> None: ...
    def wizard_changed(self, snapshot: dict | None) -> None: ...
    def open_url(self, url: str) -> None: ...


class Router:
    """Owns the context stack and executes every action.

    The base context follows the foreground window ("discord" or "game");
    Discord popups and our own overlays are pushed on top of it.
    """

    def __init__(
        self,
        cfg,
        keys: Keys,
        discord: Discord,
        ui: Ui,
        t: Callable[..., str],
        schedule: Callable[[float, Callable[[], None]], None],
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.keys = keys
        self.discord = discord
        self.ui = ui
        self.t = t
        self.schedule = schedule
        self.clock = clock
        # Called after the setup assistant changed the overlay key, so it can be registered again.
        self.on_keys_changed: Callable[[], None] | None = None
        # Called after the setup assistant changed the autostart mode, so Windows' entry can follow.
        self.on_autostart_changed: Callable[[], None] | None = None
        self.stack: list[str] = []
        self.context = ""
        self.menu = MenuModel()
        self.wizard = WizardModel()
        self._pending: str | None = None  # action waiting for the confirmation dialog
        self._launch_deadline = 0.0
        self._next_launch_probe = 0.0
        self._next_wizard_refresh = 0.0
        self._handlers = self._build_handlers()
        self.apply_config(cfg)

    def apply_config(self, cfg) -> None:
        self.cfg = cfg
        self.profile = load_profile(cfg.bindings, normalize_action)
        self.gestures = GestureEngine(cfg.timing)
        if cfg.osk_layout in LETTER_ROWS:
            layout = cfg.osk_layout
        else:
            layout = "de" if getattr(self.t, "lang", "en") == "de" else "en"
        labels = {key: self.t(f"osk.{key}") for key in ("space", "insert", "send", "placeholder")}
        self.osk = OskModel(layout, labels)
        self._close_layers()
        self.context = ""  # forces a hint refresh on the next tick

    @property
    def fast_polling(self) -> bool:
        """In a game only the overlay chord matters, so input can be polled less often."""
        return self.context != "game"

    def handles(self, action: str) -> bool:
        return action in self._handlers

    # --- entry points ---------------------------------------------------------

    def tick(self, pressed: frozenset[str]) -> None:
        now = self.clock()
        self._probe_launch(now)
        context = self._resolve_context()
        if context != self.context:
            log.debug("Context %s -> %s", self.context or "-", context)
            for fired in self.gestures.consume_all():
                self._run(fired)
            self.context = context
            self.ui.context_changed(context, hints.build(self.profile.get(context, _EMPTY), self.t))
        if context == "wizard" and self.wizard.step.id == "discord" and now >= self._next_wizard_refresh:
            self._next_wizard_refresh = now + 1.0
            self._wizard_publish()
        for fired in self.gestures.update(pressed, now, self.profile.get(context, _EMPTY)):
            self._run(fired)

    def on_hotkey(self, name: str) -> None:
        if name != "overlay":
            return
        if self.stack and self.stack[-1] == "wizard" and self.wizard.step.id == "overlay":
            # The user is testing the button they just mapped.
            self.ui.toast(self.t("toast.key_detected", key=self.cfg.handheld_keys["overlay"]))
            return
        self._run(Fired("overlay.toggle"))

    def open_wizard(self, step: str = "") -> None:
        self._wizard_open(step)

    def open_support(self) -> None:
        self._run(Fired("app.support"))

    def osk_tap(self, row: int, col: int) -> None:
        if "osk" in self.stack and self.osk.select(row, col):
            self._osk_press()

    def menu_tap(self, index: int) -> None:
        if "menu" in self.stack and self.menu.select(index):
            self._menu_select()

    def confirm_answer(self, yes: bool) -> None:
        if "confirm" in self.stack:
            self._run(Fired("confirm.yes" if yes else "confirm.no"))

    def wizard_button(self, which: str) -> None:
        action = {
            "primary": "wizard.primary",
            "secondary": "wizard.secondary",
            "back": "wizard.back",
            "next": "wizard.next",
            "collapse": "wizard.collapse",
            "move": "wizard.move",
            "key_prev": "wizard.key_prev",
            "key_next": "wizard.key_next",
        }.get(which)
        if action and "wizard" in self.stack:
            self._run(Fired(action))

    # --- context --------------------------------------------------------------

    def _resolve_context(self) -> str:
        in_discord = self.discord.is_discord(self.discord.foreground())
        if not in_discord and any(name in self.stack for name in DISCORD_LAYERS):
            self._close_layers()
        if self.stack:
            return self.stack[-1]
        return "discord" if in_discord else "game"

    def _push(self, name: str) -> None:
        if name in self.stack:
            self.stack.remove(name)
        self.stack.append(name)

    def _pop(self, name: str) -> None:
        if name in self.stack:
            self.stack.remove(name)

    def _close_layers(self) -> None:
        for name in DISCORD_LAYERS:
            self._pop(name)
        self._pending = None
        self.ui.osk_changed(None)
        self.ui.menu_changed(None)
        self.ui.confirm_changed(None)

    # --- dispatch -------------------------------------------------------------

    def _run(self, fired: Fired) -> None:
        action, phase = fired.action, fired.phase
        log.debug("Action %s (%s) in %s", action, phase, self.context)
        try:
            if action.startswith("key:"):
                {"fire": self.keys.tap, "down": self.keys.down, "up": self.keys.up}[phase](action[4:])
            elif action == "voice.ptt" and phase != "fire":
                combo = self.cfg.handheld_keys["ptt"]
                if combo:
                    (self.keys.down if phase == "down" else self.keys.up)(combo)
            elif phase != "fire":
                return
            elif action.startswith("text:"):
                self.keys.type_text(action[5:])
            elif action.startswith("reply:"):
                self._reply(int(action[6:]))
            elif action.startswith("favorite:"):
                self._favorite(int(action[9:]))
            elif action in self._handlers:
                self._handlers[action]()
            else:
                log.warning("Unknown action %r", action)
        except Exception:
            log.exception("Action %r failed", action)

    def _build_handlers(self) -> dict[str, Callable[[], None]]:
        return {
            "overlay.toggle": self._toggle_overlay,
            "app.support": self._open_support,
            "voice.mute": self._mute,
            "voice.ptt": lambda: self._tap(self.cfg.handheld_keys["ptt"]),
            "voice.leave": lambda: self._ask("confirm.leave", "voice.disconnect"),
            "voice.disconnect": lambda: self._tap(self.cfg.discord_keybinds["disconnect"]),
            "discord.switcher": lambda: self._open_popup("switcher"),
            "discord.voice_channels": self._voice_channels,
            "discord.emoji": lambda: self._open_popup("emoji"),
            "discord.settings": self._open_settings,
            "popup.accept": lambda: self._close_popup("Enter"),
            "popup.close": lambda: self._close_popup("Esc"),
            "confirm.yes": lambda: self._answer(True),
            "confirm.no": lambda: self._answer(False),
            "osk.open": self._osk_open,
            "osk.close": self._osk_close,
            "osk.up": lambda: self._osk_edit(lambda osk: osk.move(-1, 0)),
            "osk.down": lambda: self._osk_edit(lambda osk: osk.move(1, 0)),
            "osk.left": lambda: self._osk_edit(lambda osk: osk.move(0, -1)),
            "osk.right": lambda: self._osk_edit(lambda osk: osk.move(0, 1)),
            "osk.press": self._osk_press,
            "osk.backspace": lambda: self._osk_edit(OskModel.backspace),
            "osk.space": lambda: self._osk_edit(lambda osk: osk.insert(" ")),
            "osk.shift": lambda: self._osk_edit(OskModel.toggle_shift),
            "osk.symbols": lambda: self._osk_edit(OskModel.toggle_symbols),
            "osk.cursor_left": lambda: self._osk_edit(OskModel.cursor_left),
            "osk.cursor_right": lambda: self._osk_edit(OskModel.cursor_right),
            "osk.insert": lambda: self._osk_commit(send=False),
            "osk.send": lambda: self._osk_commit(send=True),
            "menu.open": self._menu_open,
            "menu.close": self._menu_close,
            "menu.up": lambda: self._menu_move(-1),
            "menu.down": lambda: self._menu_move(1),
            "menu.select": self._menu_select,
            "wizard.open": self._wizard_open,
            "wizard.close": self._wizard_close,
            "wizard.primary": self._wizard_primary,
            "wizard.secondary": self._wizard_secondary,
            "wizard.next": lambda: self._wizard_move(self.wizard.next),
            "wizard.prev": lambda: self._wizard_move(self.wizard.prev),
            "wizard.back": self._wizard_back,
            "wizard.key_prev": lambda: self._wizard_pick(-1),
            "wizard.key_next": lambda: self._wizard_pick(1),
            "wizard.collapse": lambda: self._wizard_change(self.wizard.toggle_collapsed),
            "wizard.move": lambda: self._wizard_change(self.wizard.move),
        }

    def _tap(self, combo: str) -> None:
        if combo:
            self.keys.tap(combo)

    # --- Discord window and voice ---------------------------------------------

    def _toggle_overlay(self) -> None:
        self._close_layers()
        self._after_show(self.discord.toggle())

    def _after_show(self, result: str) -> None:
        if result == "launching":
            self._launch_deadline = self.clock() + LAUNCH_TIMEOUT_S
            self.ui.toast(self.t("toast.launching"))
        elif result == "missing":
            self.ui.toast(self.t("toast.not_found"))
        elif result == "failed":
            self.ui.toast(self.t("toast.focus_failed"))

    def _open_support(self) -> None:
        """The support Discord's invite opens in the browser, which offers to continue in the app."""
        self.ui.open_url(SUPPORT_URL)
        self.ui.toast(self.t("toast.support"))

    def _probe_launch(self, now: float) -> None:
        """After starting Discord, bring its window to the front once it exists."""
        if not self._launch_deadline or now < self._next_launch_probe:
            return
        if now > self._launch_deadline:
            self._launch_deadline = 0.0
            return
        self._next_launch_probe = now + 0.5
        if self.discord.find():
            self._launch_deadline = 0.0
            self.discord.show()

    def _mute(self) -> None:
        # The global keybind recorded in the setup assistant works in Discord and in games.
        combo = self.cfg.handheld_keys["mute"]
        if combo:
            self.keys.tap(combo)
            self.ui.toast(self.t("toast.mute"))

    def _voice_channels(self) -> None:
        """After "!" Discord's quick switcher lists only voice channels; Enter joins the chosen one."""
        self._open_popup("switcher")
        self.schedule(SWITCHER_TYPE_DELAY_S, lambda: self.keys.type_text("!"))

    def _open_settings(self) -> None:
        result = self.discord.show()
        self._after_show(result)
        if result == "discord":
            self.schedule(SETTINGS_DELAY_S, lambda: self.keys.tap(self.cfg.discord_shortcuts["settings"]))

    def _open_popup(self, shortcut: str) -> None:
        self.keys.tap(self.cfg.discord_shortcuts[shortcut])
        self._push("discord_popup")

    def _close_popup(self, key: str) -> None:
        self.keys.tap(key)
        self._pop("discord_popup")

    def _ask(self, question: str, action: str) -> None:
        """Show a yes/no dialog (Ⓐ/Ⓑ); the action only runs on yes."""
        self._pending = action
        self._push("confirm")
        self.ui.confirm_changed({
            "title": self.t(f"{question}.title"),
            "body": self.t(f"{question}.body"),
            "yes": self.t("confirm.yes"),
            "no": self.t("confirm.no"),
        })

    def _answer(self, yes: bool) -> None:
        action, self._pending = self._pending, None
        self._pop("confirm")
        self.ui.confirm_changed(None)
        if yes and action:
            self._run(Fired(action))

    def _reply(self, index: int) -> None:
        replies = self.cfg.quick_replies
        if 0 <= index < len(replies):
            self.keys.type_text(replies[index])
            self.keys.tap("Enter")

    def _favorite(self, index: int) -> None:
        """Favorites go through Discord's quick switcher: Ctrl+K, type the query, Enter."""
        favorites = self.cfg.favorites
        if not 0 <= index < len(favorites):
            return
        query = favorites[index]["query"]
        self.keys.tap(self.cfg.discord_shortcuts["switcher"])
        self.schedule(SWITCHER_TYPE_DELAY_S, lambda: self.keys.type_text(query))
        self.schedule(SWITCHER_ENTER_DELAY_S, lambda: self.keys.tap("Enter"))

    # --- on-screen keyboard ---------------------------------------------------

    def _osk_open(self) -> None:
        self._push("osk")
        self.ui.osk_changed(self.osk.snapshot())

    def _osk_close(self) -> None:
        self._pop("osk")
        self.ui.osk_changed(None)

    def _osk_edit(self, change: Callable[[OskModel], object]) -> None:
        change(self.osk)
        self.ui.osk_changed(self.osk.snapshot())

    def _osk_press(self) -> None:
        result = self.osk.press()
        if result:
            self._osk_commit(send=result == "send")
        else:
            self.ui.osk_changed(self.osk.snapshot())

    def _osk_commit(self, send: bool) -> None:
        text = self.osk.text
        self.osk.clear()
        self._osk_close()
        if text:
            self.keys.type_text(text)
        if send:
            self.keys.tap("Enter")
            self._pop("discord_popup")  # Enter also picks the quick switcher result

    # --- quick menu -----------------------------------------------------------

    def _menu_items(self) -> list[MenuItem]:
        t = self.t
        items = [MenuItem(text, f"reply:{i}", t("menu.section.replies")) for i, text in enumerate(self.cfg.quick_replies)]
        items += [
            MenuItem(fav["name"], f"favorite:{i}", t("menu.section.favorites"))
            for i, fav in enumerate(self.cfg.favorites)
        ]
        voice, app = t("menu.section.voice"), t("menu.section.app")
        items += [
            MenuItem(t("menu.mute"), "voice.mute", voice),
            MenuItem(t("menu.voice_channels"), "discord.voice_channels", voice),
            MenuItem(t("menu.leave"), "voice.leave", voice),
            MenuItem(t("menu.to_game"), "overlay.toggle", app),
            MenuItem(t("menu.setup"), "wizard.open", app),
            MenuItem(t("menu.support"), "app.support", app),
        ]
        return items

    def _menu_open(self) -> None:
        footer = self.t("app.credit", version=__version__, author=__author__)
        self.menu.open(self.t("menu.title"), self._menu_items(), footer)
        self._push("menu")
        self.ui.menu_changed(self.menu.snapshot())

    def _menu_close(self) -> None:
        self._pop("menu")
        self.ui.menu_changed(None)

    def _menu_move(self, delta: int) -> None:
        self.menu.move(delta)
        self.ui.menu_changed(self.menu.snapshot())

    def _menu_select(self) -> None:
        item = self.menu.current
        self._menu_close()
        if item:
            self._run(Fired(item.action))

    # --- setup assistant ------------------------------------------------------

    def _wizard_keys(self) -> dict[str, str]:
        """Everything the assistant records or shows: the handheld keys plus the leave-call keybind."""
        keys = dict(self.cfg.handheld_keys)
        keys["leave"] = self.cfg.discord_keybinds["disconnect"]
        return keys

    def _wizard_open(self, step: str = "") -> None:
        self.wizard.start(step)
        self._push("wizard")
        self._wizard_publish()

    def _wizard_close(self) -> None:
        self._pop("wizard")
        self.ui.wizard_changed(None)
        if not self.cfg.setup_done or self.cfg.setup_step:
            self.cfg.mark_setup_done()

    def _wizard_move(self, move: Callable[[], bool]) -> None:
        if move():
            self._wizard_publish()

    def _wizard_change(self, change: Callable[[], None]) -> None:
        change()
        self._wizard_publish()

    def _wizard_back(self) -> None:
        if self.wizard.prev():
            self._wizard_publish()
        else:
            self._wizard_close()

    def _wizard_primary(self) -> None:
        action = self.wizard.step.primary
        if action is None:
            self._wizard_move(self.wizard.next)
        else:
            self._wizard_action(action)

    def _wizard_secondary(self) -> None:
        if self.wizard.step.secondary:
            self._wizard_action(self.wizard.step.secondary)

    def _wizard_action(self, action: str) -> None:
        if action == "close":
            self._wizard_close()
        elif action == "discord.show":
            self._after_show(self.discord.show())
            self._wizard_publish()
        elif action == "discord.settings":
            self._open_settings()
        elif action == "record":
            # Goes to the foreground window, which must be Discord's "Record Keybind" field.
            combo = self._wizard_keys().get(self.wizard.step.record or "", "")
            if not combo:
                return
            if not self.discord.is_discord(self.discord.foreground()):
                self.ui.toast(self.t("toast.discord_first"))
                return
            self.keys.tap(combo)
            self.ui.toast(self.t("toast.sent", key=combo))
        elif action == "test.mute":
            combo = self.cfg.handheld_keys["mute"]
            if not combo:
                return
            if self.discord.is_discord(self.discord.foreground()):
                # Discord ignores its keybinds while the keybind settings are open, so leave them first.
                self.keys.tap("Esc")
                self.schedule(SETTINGS_DELAY_S, lambda: self.keys.tap(combo))
            else:
                self.keys.tap(combo)
            self.ui.toast(self.t("toast.sent", key=combo))

    def _wizard_pick(self, delta: int) -> None:
        """◀ ▶ change the step's handheld key or setting."""
        step = self.wizard.step
        if step.key:
            self._pick_key(step.key, delta)
        elif step.option == "autostart":
            modes = AUTOSTART_MODES
            self.cfg.set_autostart(modes[(modes.index(self.cfg.autostart) + delta) % len(modes)])
            if self.on_autostart_changed:
                self.on_autostart_changed()
        else:
            return
        self._wizard_publish()

    def _pick_key(self, name: str, delta: int) -> None:
        """Cycle a handheld key through F1-F12, skipping keys used for something else."""
        keys = self.cfg.handheld_keys
        taken = {value for other, value in keys.items() if other != name}
        choices = [key for key in KEY_CHOICES if key not in taken]
        current = keys.get(name)
        if current in choices:
            new = choices[(choices.index(current) + delta) % len(choices)]
        else:
            new = choices[0] if delta > 0 else choices[-1]
        self.cfg.set_handheld_key(name, new)
        if name == "overlay" and self.on_keys_changed:
            self.on_keys_changed()

    def _wizard_publish(self) -> None:
        status = self.t("wizard.status.found" if self.discord.find() else "wizard.status.missing")
        options = {"autostart": self.cfg.autostart}
        self.ui.wizard_changed(self.wizard.snapshot(self.t, self._wizard_keys(), options, status=status))
