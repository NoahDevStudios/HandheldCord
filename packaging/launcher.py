"""Entry point of the frozen build (PyInstaller needs a script, not a package)."""
from handheldcord.app import main

raise SystemExit(main())
