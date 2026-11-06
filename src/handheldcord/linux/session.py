"""Desktop session helpers: a single running instance and opening files."""
from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path

log = logging.getLogger(__name__)

_lock: int | None = None  # stays open while HandheldCord runs


def acquire_single_instance(name: str = "handheldcord") -> int:
    """Return a lock handle, or 0 if another instance already holds it."""
    global _lock
    import fcntl

    runtime = os.environ.get("XDG_RUNTIME_DIR")
    path = Path(runtime, f"{name}.lock") if runtime else Path("/tmp", f"{name}-{os.getuid()}.lock")
    try:
        fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
    except OSError:
        log.warning("Could not create the single-instance lock %s", path, exc_info=True)
        return -1
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        os.close(fd)
        return 0
    _lock = fd
    return fd


def open_file(path: Path) -> None:
    try:
        subprocess.Popen(["xdg-open", str(path)], start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        log.warning("Could not open %s - xdg-open is missing", path)
