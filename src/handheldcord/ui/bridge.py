"""The QObject exposed to QML as "hc": overlay state goes in, touch input comes out."""
from __future__ import annotations

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices

# The hint bar is only useful while Discord or one of our overlays is in front.
HINT_CONTEXTS = frozenset({"discord", "discord_popup", "osk", "menu", "confirm"})


class Bridge(QObject):
    hintsChanged = Signal()
    toastChanged = Signal()
    oskChanged = Signal()
    oskRowsChanged = Signal()
    menuChanged = Signal()
    menuItemsChanged = Signal()
    confirmChanged = Signal()
    wizardChanged = Signal()
    # Emitted on the hotkey thread; Qt delivers it queued on the GUI thread.
    hotkeyPressed = Signal(str)

    def __init__(self, show_hints: bool = True) -> None:
        super().__init__()
        self.router = None
        self.show_hints = show_hints
        self._hints: list = []
        self._hints_visible = False
        self._toast = ""
        self._osk: dict = {"visible": False}
        self._osk_rows: list = []
        self._menu: dict = {"visible": False}
        self._menu_items: list = []
        self._confirm: dict = {"visible": False}
        self._wizard: dict = {"visible": False}
        self.hotkeyPressed.connect(self._on_hotkey)

    # --- called by the router -------------------------------------------------

    def context_changed(self, context: str, hint_list: list[dict]) -> None:
        self._hints = hint_list
        self._hints_visible = self.show_hints and context in HINT_CONTEXTS and bool(hint_list)
        self.hintsChanged.emit()

    def toast(self, text: str) -> None:
        self._toast = text
        self.toastChanged.emit()

    def osk_changed(self, snapshot: dict | None) -> None:
        if snapshot is None:
            if not self._osk.get("visible"):
                return
            self._osk = {"visible": False}
        else:
            state = dict(snapshot)
            rows = state.pop("rows")
            # Only rebuild the keys when the layer changes, not on every highlight move.
            if rows != self._osk_rows:
                self._osk_rows = rows
                self.oskRowsChanged.emit()
            self._osk = {**state, "visible": True}
        self.oskChanged.emit()

    def menu_changed(self, snapshot: dict | None) -> None:
        if snapshot is None:
            if not self._menu.get("visible"):
                return
            self._menu = {"visible": False}
        else:
            state = dict(snapshot)
            items = state.pop("items")
            if items != self._menu_items:
                self._menu_items = items
                self.menuItemsChanged.emit()
            self._menu = {**state, "visible": True}
        self.menuChanged.emit()

    def confirm_changed(self, snapshot: dict | None) -> None:
        if snapshot is None and not self._confirm.get("visible"):
            return
        self._confirm = {**snapshot, "visible": True} if snapshot else {"visible": False}
        self.confirmChanged.emit()

    def wizard_changed(self, snapshot: dict | None) -> None:
        self._wizard = {**snapshot, "visible": True} if snapshot else {"visible": False}
        self.wizardChanged.emit()

    def open_url(self, url: str) -> None:
        QDesktopServices.openUrl(QUrl(url))

    # --- properties read by QML -----------------------------------------------

    hints = Property("QVariantList", lambda self: self._hints, notify=hintsChanged)
    hintsVisible = Property(bool, lambda self: self._hints_visible, notify=hintsChanged)
    toastText = Property(str, lambda self: self._toast, notify=toastChanged)
    osk = Property("QVariantMap", lambda self: self._osk, notify=oskChanged)
    oskRows = Property("QVariantList", lambda self: self._osk_rows, notify=oskRowsChanged)
    menu = Property("QVariantMap", lambda self: self._menu, notify=menuChanged)
    menuItems = Property("QVariantList", lambda self: self._menu_items, notify=menuItemsChanged)
    confirm = Property("QVariantMap", lambda self: self._confirm, notify=confirmChanged)
    wizard = Property("QVariantMap", lambda self: self._wizard, notify=wizardChanged)

    # --- touch input from QML -------------------------------------------------

    @Slot(int, int)
    def oskTap(self, row: int, col: int) -> None:
        if self.router:
            self.router.osk_tap(row, col)

    @Slot(int)
    def menuTap(self, index: int) -> None:
        if self.router:
            self.router.menu_tap(index)

    @Slot(bool)
    def confirmAnswer(self, yes: bool) -> None:
        if self.router:
            self.router.confirm_answer(yes)

    @Slot(str)
    def wizardButton(self, which: str) -> None:
        if self.router:
            self.router.wizard_button(which)

    @Slot(str)
    def _on_hotkey(self, name: str) -> None:
        if self.router:
            self.router.on_hotkey(name)
