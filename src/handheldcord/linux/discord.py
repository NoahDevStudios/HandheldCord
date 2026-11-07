"""Finds the Discord app's main window (X11/XWayland) and switches between it and the game.

Since Electron 38, Electron apps such as Discord start as native Wayland apps on Wayland desktops.
HandheldCord can neither see nor control those, so it starts Discord in X11 mode and offers to
switch a running Wayland Discord over (permanently, for later starts too).
"""
from __future__ import annotations

import logging
import os
import shutil
import signal
import subprocess
import threading
import time
from pathlib import Path

from .x11 import X11

log = logging.getLogger(__name__)

DISCORD_CLASSES = frozenset({"discord", "discordptb", "discordcanary"})  # WM_CLASS, also of the Flatpak
DISCORD_PROCESSES = frozenset({"discord", "discordptb", "discordcanary"})  # /proc/<pid>/comm
COMMANDS = ("discord", "discord-ptb", "discord-canary")
FLATPAKS = ("com.discordapp.Discord", "com.discordapp.DiscordCanary")
X11_FLAG = "--ozone-platform=x11"
CACHE_TTL_S = 5.0
STARTUP_S = 30.0  # a Discord we started may run for a while before its window exists
QUIT_TIMEOUT_S = 15.0


class DiscordWindows:
    def __init__(self, maximize: bool = True, dry_run: bool = False) -> None:
        self.maximize = maximize
        self.dry_run = dry_run
        self.x = X11()
        self._previous = 0
        self._cache: dict[int, tuple[bool, float]] = {}
        self._launched_at = -STARTUP_S
        self._last_status = ""
        log.info(
            "Session %s, desktop %s, window manager %s, Discord running: %s",
            os.environ.get("XDG_SESSION_TYPE", "?"), os.environ.get("XDG_CURRENT_DESKTOP", "?"),
            self.x.window_manager() or "none (no EWMH)", self.running(),
        )

    def foreground(self) -> int:
        return self.x.active_window()

    def running(self) -> bool:
        """Whether a Discord process exists, even before (or without) an X11 window."""
        return bool(discord_pids())

    def status(self) -> str:
        """ "found", "missing", "starting" (we just started it) or "wayland" (runs without an X11 window)."""
        if self.find():
            status = "found"
        elif not self.running():
            status = "missing"
        elif time.monotonic() - self._launched_at < STARTUP_S:
            status = "starting"
        else:
            status = "wayland"
        if status != self._last_status:
            self._last_status = status
            details = ", ".join(f"{pid}: {_exe(pid) or '?'}" for pid in discord_pids()) or "no process"
            log.info("Discord %s (%s)", status, details)
        return status

    def is_discord(self, wid: int) -> bool:
        """Checked every input tick, so the lookup is cached per window."""
        if not wid:
            return False
        now = time.monotonic()
        cached = self._cache.get(wid)
        if cached and cached[1] > now:
            return cached[0]
        result = self.x.wm_class(wid) in DISCORD_CLASSES
        if len(self._cache) > 256:
            self._cache.clear()
        self._cache[wid] = (result, now + CACHE_TTL_S)
        return result

    def find(self) -> int:
        """The main window: a titled Discord window, preferring visible and large ones."""
        best, best_score = 0, (False, -1)
        for wid in self.x.client_windows():
            if not self.is_discord(wid) or not self.x.title(wid):
                continue
            score = (not self.x.is_minimized(wid), self.x.area(wid))
            if score > best_score:
                best, best_score = wid, score
        return best

    def show(self) -> str:
        """Bring Discord to the front, starting it if needed.

        Returns "discord", "launching", "missing" or "wayland" (it runs, but HandheldCord can't see it).
        """
        wid = self.find()
        if not wid:
            if self.running():
                return "launching" if time.monotonic() - self._launched_at < STARTUP_S else "wayland"
            return "launching" if self._launch() else "missing"
        current = self.x.active_window()
        if current and current != wid and self.x.pid(current) != os.getpid():
            self._previous = current
        if self.dry_run:
            log.info("[dry-run] would bring Discord (%#x) to the front", wid)
            return "discord"
        if self.maximize and not self.x.is_maximized(wid):
            self.x.maximize(wid)
        self.x.activate(wid)
        return "discord"

    def toggle(self) -> str:
        if self.is_discord(self.x.active_window()):
            return self.back()
        return self.show()

    def back(self) -> str:
        """Return to the window that was active before Discord; returns "game" or "minimized"."""
        previous = self._previous
        if self.dry_run:
            log.info("[dry-run] would return to %#x", previous)
            return "game"
        if self.x.exists(previous) and not self.is_discord(previous):
            self.x.activate(previous)
            return "game"
        current = self.x.active_window()
        if current:
            self.x.minimize(current)
        return "minimized"

    def restart_in_x11(self) -> str:
        """Quit a Discord that runs as a Wayland app and start it again in X11 mode, for good."""
        pids = discord_pids()
        flatpak = any(_exe(pid).startswith("/app/") for pid in pids)
        if self.dry_run:
            log.info("[dry-run] would restart Discord in X11 mode (Flatpak: %s)", flatpak)
            return "launching"
        log.info("Restarting Discord in X11 mode (Flatpak: %s)", flatpak)
        make_x11_permanent(flatpak)
        for pid in pids:
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError:
                pass
        self._launched_at = time.monotonic()
        threading.Thread(target=self._launch_when_gone, args=(pids, flatpak), daemon=True).start()
        return "launching"

    def _launch_when_gone(self, pids: list[int], flatpak: bool) -> None:
        deadline = time.monotonic() + QUIT_TIMEOUT_S
        while time.monotonic() < deadline and any(Path("/proc", str(pid)).exists() for pid in pids):
            time.sleep(0.2)
        self._launch(prefer_flatpak=flatpak)

    def _launch(self, prefer_flatpak: bool = False) -> bool:
        if self.dry_run:
            log.info("[dry-run] would start Discord")
            return True
        command = launch_command(prefer_flatpak)
        if command is None:
            log.warning("Discord does not seem to be installed")
            return False
        self._launched_at = time.monotonic()
        return _spawn(command)


def discord_pids() -> list[int]:
    pids = []
    for comm in Path("/proc").glob("[0-9]*/comm"):
        try:
            if comm.read_text().strip().lower() in DISCORD_PROCESSES:
                pids.append(int(comm.parent.name))
        except (OSError, ValueError):
            continue
    return pids


def launch_command(prefer_flatpak: bool = False) -> list[str] | None:
    """How to start Discord in X11 mode: the installed package or the Flatpak."""
    native = next((path for path in map(shutil.which, COMMANDS) if path), None)
    flatpak = shutil.which("flatpak")
    app_id = next((app for app in FLATPAKS if _flatpak_installed(app)), None) if flatpak else None
    commands = []
    if native:
        commands.append([native, X11_FLAG])
    if app_id:
        flatpak_command = [flatpak, "run", "--nosocket=wayland", "--env=XDG_SESSION_TYPE=x11", app_id, X11_FLAG]
        commands.insert(0 if prefer_flatpak else len(commands), flatpak_command)
    return commands[0] if commands else None


def make_x11_permanent(flatpak: bool) -> None:
    """Later starts from the app menu or Discord's own autostart should use X11 mode as well."""
    if flatpak:
        for app_id in FLATPAKS:
            if _flatpak_installed(app_id):
                subprocess.run(
                    ["flatpak", "override", "--user", "--nosocket=wayland", "--env=XDG_SESSION_TYPE=x11", app_id],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
                )
        return
    data = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share")
    config = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    shared = os.environ.get("XDG_DATA_DIRS") or "/usr/local/share:/usr/share"
    system_dirs = [Path(d, "applications") for d in shared.split(":") if d]
    for directory in (*system_dirs, data / "applications", config / "autostart"):
        for entry in directory.glob("discord*.desktop"):
            # System-wide entries get a copy in the user's folder, which takes precedence over them.
            target = entry if entry.is_relative_to(Path.home()) else data / "applications" / entry.name
            if target != entry and target.exists():
                continue
            try:
                text = entry.read_text(encoding="utf-8")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(with_x11_flag(text), encoding="utf-8")
            except OSError:
                log.warning("Could not switch %s to X11 mode", entry, exc_info=True)


def with_x11_flag(desktop_entry: str) -> str:
    """Add the X11 flag to every Exec line of a desktop entry that lacks it."""
    lines = []
    for line in desktop_entry.splitlines():
        if line.startswith("Exec=") and "--ozone-platform" not in line:
            line += f" {X11_FLAG}"
        lines.append(line)
    return "\n".join(lines) + "\n"


def _exe(pid: int) -> str:
    try:
        return os.readlink(f"/proc/{pid}/exe")
    except OSError:
        return ""


def _flatpak_installed(app_id: str) -> bool:
    return any(Path(base, app_id).is_dir() for base in (
        "/var/lib/flatpak/app", Path.home() / ".local/share/flatpak/app",
    ))


def _spawn(command: list[str]) -> bool:
    log.info("Starting %s", " ".join(command))
    try:
        subprocess.Popen(command, start_new_session=True, stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        log.warning("Could not start %s", command[0], exc_info=True)
        return False
    return True
