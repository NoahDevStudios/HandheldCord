"""Entry point: wires controller input, the router, Win32 and the QML overlays together."""
from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from PySide6.QtCore import QLocale, Qt, QTimer, QUrl
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from . import __version__, config
from .companion.actions import DEFAULT_BINDINGS
from .companion.discord_window import DiscordWindows
from .companion.router import Router
from .i18n import Translator, resolve_language
from .input.normalize import Normalizer
from .input.xinput import XInputBackend
from .ui.bridge import Bridge
from .ui.icon import render_icon
from .ui.overlay import OVERLAYS, QML_DIR, prepare_overlay
from .windows import win32
from .windows.hotkeys import GlobalHotkeys
from .windows.sender import KeySender

log = logging.getLogger("handheldcord")

FAST_POLL_MS = 16  # ~60 Hz while Discord or one of our overlays is in front
SLOW_POLL_MS = 33  # in a game only the overlay chord is watched


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    config_path = Path(args.config) if args.config else config.DEFAULT_PATH
    _setup_logging(config_path.parent, args.debug)
    log.info("HandheldCord %s starting (companion mode)", __version__)
    if not win32.acquire_single_instance():
        log.info("HandheldCord is already running")
        return 0

    cfg = config.load(config_path)
    _write_reference_bindings(config_path.parent)

    app = QApplication(sys.argv[:1])
    app.setQuitOnLastWindowClosed(False)
    t = Translator(resolve_language(cfg.language, QLocale.system().name()))

    bridge = Bridge(show_hints=cfg.show_hints)
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("hc", bridge)
    for name, click_through in OVERLAYS:
        loaded = len(engine.rootObjects())
        engine.load(QUrl.fromLocalFile(str(QML_DIR / f"{name}.qml")))
        if len(engine.rootObjects()) == loaded:
            log.error("Could not load %s.qml", name)
            return 1
        prepare_overlay(engine.rootObjects()[-1], click_through)

    keys = KeySender(dry_run=args.dry_run)
    discord = DiscordWindows(maximize=cfg.maximize_discord, dry_run=args.dry_run)
    router = Router(
        cfg, keys, discord, bridge, t,
        schedule=lambda delay, callback: QTimer.singleShot(int(delay * 1000), callback),
    )
    bridge.router = router
    if cfg.error:
        bridge.toast(t("toast.config_error"))

    backend = XInputBackend()
    normalizer = Normalizer()
    timer = QTimer()
    timer.setTimerType(Qt.TimerType.PreciseTimer)
    last_pressed: frozenset[str] = frozenset()

    def tick() -> None:
        nonlocal last_pressed
        try:
            pressed = normalizer.update(backend.poll())
            if args.debug_input and pressed != last_pressed:
                log.info("Buttons: %s", " ".join(sorted(pressed)) or "-")
            last_pressed = pressed
            router.tick(pressed)
        except Exception:
            log.exception("Input tick failed")
        interval = FAST_POLL_MS if router.fast_polling else SLOW_POLL_MS
        if timer.interval() != interval:
            timer.setInterval(interval)

    timer.timeout.connect(tick)
    timer.start(FAST_POLL_MS)

    hotkeys = GlobalHotkeys(bridge.hotkeyPressed.emit)
    hotkeys.start({"overlay": cfg.overlay_hotkey})

    def reload_config() -> None:
        new_cfg = config.load(config_path)
        router.apply_config(new_cfg)
        discord.maximize = new_cfg.maximize_discord
        bridge.show_hints = new_cfg.show_hints
        hotkeys.start({"overlay": new_cfg.overlay_hotkey})
        bridge.toast(t("toast.config_error" if new_cfg.error else "toast.config_reloaded"))

    tray, tray_menu = _create_tray(app, t, router, config_path, reload_config)
    if args.wizard or not cfg.setup_done:
        QTimer.singleShot(600, router.open_wizard)
    if args.exit_after:
        QTimer.singleShot(int(args.exit_after * 1000), app.quit)

    try:
        return app.exec()
    finally:
        timer.stop()
        hotkeys.stop()
        tray.hide()
        log.info("HandheldCord stopped")


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="handheldcord",
        description="Controller-first companion for the official Discord app.",
    )
    parser.add_argument("--config", help="path to config.json (default: %%APPDATA%%\\HandheldCord\\config.json)")
    parser.add_argument("--dry-run", action="store_true", help="log key presses and window switches instead of doing them")
    parser.add_argument("--debug", action="store_true", help="verbose logging")
    parser.add_argument("--debug-input", action="store_true", help="log every controller button change")
    parser.add_argument("--wizard", action="store_true", help="open the setup assistant on start")
    parser.add_argument("--exit-after", type=float, metavar="SECONDS", help=argparse.SUPPRESS)
    parser.add_argument("--version", action="version", version=f"HandheldCord {__version__}")
    return parser.parse_args(argv)


def _setup_logging(directory: Path, debug: bool) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    handlers: list[logging.Handler] = [
        RotatingFileHandler(directory / "handheldcord.log", maxBytes=1_000_000, backupCount=2, encoding="utf-8"),
    ]
    if sys.stderr is not None:  # pythonw.exe has no console
        handlers.append(logging.StreamHandler())
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        handlers=handlers,
    )


def _write_reference_bindings(directory: Path) -> None:
    """A copy of the default layout to copy entries from when customizing "bindings"."""
    try:
        text = json.dumps(DEFAULT_BINDINGS, indent=2, ensure_ascii=False) + "\n"
        (directory / "default-bindings.json").write_text(text, encoding="utf-8")
    except OSError:
        log.warning("Could not write default-bindings.json", exc_info=True)


def _open_file(path: Path) -> None:
    try:
        os.startfile(path)
    except OSError:  # no program associated with .json
        subprocess.Popen(["notepad.exe", str(path)])


def _create_tray(app, t, router, config_path: Path, reload_config) -> tuple[QSystemTrayIcon, QMenu]:
    tray = QSystemTrayIcon(_app_icon(), app)
    tray.setToolTip(t("tray.tooltip"))
    menu = QMenu()
    entries = (
        (t("tray.setup"), router.open_wizard),
        (t("tray.config"), lambda: _open_file(config_path)),
        (t("tray.reload"), reload_config),
        None,
        (t("tray.quit"), app.quit),
    )
    for entry in entries:
        if entry is None:
            menu.addSeparator()
            continue
        label, callback = entry
        menu.addAction(label).triggered.connect(callback)
    tray.setContextMenu(menu)
    tray.show()
    return tray, menu


def _app_icon() -> QIcon:
    return QIcon(QPixmap.fromImage(render_icon(64)))
