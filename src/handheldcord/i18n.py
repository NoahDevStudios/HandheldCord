"""UI strings (English and German) and language selection."""
from __future__ import annotations

STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "hint.channel": "Channel",
        "hint.unread": "Unread",
        "hint.server": "Server",
        "hint.scroll": "Scroll",
        "hint.confirm": "OK / Send",
        "hint.back": "Back",
        "hint.search": "Search",
        "hint.emoji": "Emoji",
        "hint.write": "Write",
        "hint.menu": "Menu",
        "hint.mute": "Mute",
        "hint.deafen": "Deafen",
        "hint.ptt": "Push-to-talk",
        "hint.to_game": "Game",
        "hint.tap_long": "{tap} (hold: {long})",
        "hint.long": "hold: {label}",
        "hint.chord": "{label} (hold)",
        "hint.select": "Select",
        "hint.close": "Close",
        "hint.key": "Key",
        "hint.delete": "Delete",
        "hint.space": "Space",
        "hint.shift": "Shift",
        "hint.symbols": "Symbols",
        "hint.cursor": "Cursor",
        "hint.insert": "Insert",
        "hint.send": "Send",
        "toast.launching": "Starting Discord …",
        "toast.not_found": "Discord not found – is it installed?",
        "toast.focus_failed": "Couldn't bring the window to the front",
        "toast.mute": "Mute toggled",
        "toast.deafen": "Deafen toggled",
        "toast.sent": "Sent {key}",
        "toast.config_reloaded": "Configuration reloaded",
        "toast.config_error": "Configuration has errors – using defaults",
        "osk.space": "Space",
        "osk.insert": "Insert",
        "osk.send": "Send",
        "osk.placeholder": "Message …",
        "menu.title": "Quick menu",
        "menu.section.replies": "Quick replies",
        "menu.section.favorites": "Favorites",
        "menu.section.voice": "Voice",
        "menu.section.app": "HandheldCord",
        "menu.mute": "Toggle mute",
        "menu.deafen": "Toggle deafen",
        "menu.to_game": "Back to the game",
        "menu.setup": "Open setup",
        "tray.tooltip": "HandheldCord – companion mode",
        "tray.setup": "Setup …",
        "tray.config": "Open configuration",
        "tray.reload": "Reload configuration",
        "tray.quit": "Quit",
        "wizard.next": "Next",
        "wizard.back": "Back",
        "wizard.close": "Close",
        "wizard.status.found": "✔ Discord found",
        "wizard.status.missing": "✖ Discord not found",
        "wizard.welcome.title": "Welcome to HandheldCord",
        "wizard.welcome.body": (
            "HandheldCord controls your official Discord app with your controller. It never touches your "
            "account and doesn't modify Discord – it only presses keys for you.\n\n"
            "Setup takes about two minutes. For the steps inside Discord's settings you may use the "
            "touchscreen this one time."
        ),
        "wizard.discord.title": "Start Discord",
        "wizard.discord.body": "Start Discord and log in. Ⓐ brings Discord to the front or starts it.\n\n{status}",
        "wizard.discord.primary": "Open Discord",
        "wizard.mute.title": "Keybind for mute",
        "wizard.mute.body": (
            "To mute while you play, Discord needs a global keybind:\n\n"
            "1. In Discord, open Settings → Keybinds.\n"
            "2. Add a keybind with the action “Toggle Mute”.\n"
            "3. Tap “Record Keybind”, then press Ⓐ – HandheldCord sends {mute}.\n"
            "4. Stop recording."
        ),
        "wizard.mute.primary": "Send {mute}",
        "wizard.deafen.title": "Keybind for deafen",
        "wizard.deafen.body": (
            "Same as before, with the action “Toggle Deafen”:\n\n"
            "1. Add another keybind.\n"
            "2. Start recording and press Ⓐ – HandheldCord sends {deafen}.\n"
            "3. Stop recording."
        ),
        "wizard.deafen.primary": "Send {deafen}",
        "wizard.ptt.title": "Push-to-talk (optional)",
        "wizard.ptt.body": (
            "If you use push-to-talk: add a keybind with the action “Push to Talk (Normal)”, start "
            "recording and press Ⓐ – HandheldCord sends {ptt}. Then switch the input mode to "
            "Push to Talk under Voice & Video.\n\n"
            "No push-to-talk? Just continue with RB."
        ),
        "wizard.ptt.primary": "Send {ptt}",
        "wizard.test.title": "Test",
        "wizard.test.body": (
            "Ⓐ triggers mute via {mute}, Ⓧ deafen via {deafen}. The microphone or headphone icon in "
            "Discord should change.\n\n"
            "Nothing happens? Go back with Ⓑ and record the keybind again."
        ),
        "wizard.test.primary": "Test mute",
        "wizard.test.secondary": "Test deafen",
        "wizard.buttons.title": "Handheld buttons",
        "wizard.buttons.body": (
            "In a game the controller belongs to the game. So map these in Armoury Crate SE, Legion Space, "
            "MSI Center M or Handheld Companion:\n\n"
            "• a spare button to {overlay} – it switches between game and Discord,\n"
            "• a back button to {ptt} for push-to-talk,\n"
            "• optionally more buttons to {mute} (mute) and {deafen} (deafen).\n\n"
            "No spare buttons? Hold ⧉ and ☰ together for half a second."
        ),
        "wizard.conflicts.title": "Avoid double input",
        "wizard.conflicts.body": (
            "If Steam or Handheld Companion use your controller as mouse and keyboard on the desktop, "
            "Discord receives every input twice. Turn that desktop control off for your controller "
            "(in Steam: the desktop layout) while you use HandheldCord."
        ),
        "wizard.done.title": "All set!",
        "wizard.done.body": (
            "In a game: {overlay} or hold ⧉ + ☰ → Discord.\n"
            "In Discord: ✛ channels, LB/RB servers, Ⓨ write, Ⓧ search, ☰ menu, ⧉ mute (hold: deafen).\n\n"
            "You can reopen this setup from the menu (☰) at any time."
        ),
        "wizard.done.primary": "Let's go",
    },
    "de": {
        "hint.channel": "Kanal",
        "hint.unread": "Ungelesen",
        "hint.server": "Server",
        "hint.scroll": "Blättern",
        "hint.confirm": "OK / Senden",
        "hint.back": "Zurück",
        "hint.search": "Suchen",
        "hint.emoji": "Emoji",
        "hint.write": "Schreiben",
        "hint.menu": "Menü",
        "hint.mute": "Mute",
        "hint.deafen": "Deafen",
        "hint.ptt": "Push-to-Talk",
        "hint.to_game": "Zum Spiel",
        "hint.tap_long": "{tap} (lang: {long})",
        "hint.long": "lang: {label}",
        "hint.chord": "{label} (halten)",
        "hint.select": "Auswählen",
        "hint.close": "Schließen",
        "hint.key": "Taste",
        "hint.delete": "Löschen",
        "hint.space": "Leerzeichen",
        "hint.shift": "Groß",
        "hint.symbols": "Symbole",
        "hint.cursor": "Cursor",
        "hint.insert": "Einfügen",
        "hint.send": "Senden",
        "toast.launching": "Discord wird gestartet …",
        "toast.not_found": "Discord nicht gefunden – ist es installiert?",
        "toast.focus_failed": "Fenster konnte nicht nach vorne geholt werden",
        "toast.mute": "Mute umgeschaltet",
        "toast.deafen": "Deafen umgeschaltet",
        "toast.sent": "{key} gesendet",
        "toast.config_reloaded": "Konfiguration neu geladen",
        "toast.config_error": "Konfiguration fehlerhaft – Standardwerte aktiv",
        "osk.space": "Leerzeichen",
        "osk.insert": "Einfügen",
        "osk.send": "Senden",
        "osk.placeholder": "Nachricht …",
        "menu.title": "Schnellmenü",
        "menu.section.replies": "Schnellantworten",
        "menu.section.favorites": "Favoriten",
        "menu.section.voice": "Voice",
        "menu.section.app": "HandheldCord",
        "menu.mute": "Mute umschalten",
        "menu.deafen": "Deafen umschalten",
        "menu.to_game": "Zurück zum Spiel",
        "menu.setup": "Einrichtung öffnen",
        "tray.tooltip": "HandheldCord – Begleitmodus",
        "tray.setup": "Einrichtung …",
        "tray.config": "Konfiguration öffnen",
        "tray.reload": "Konfiguration neu laden",
        "tray.quit": "Beenden",
        "wizard.next": "Weiter",
        "wizard.back": "Zurück",
        "wizard.close": "Schließen",
        "wizard.status.found": "✔ Discord gefunden",
        "wizard.status.missing": "✖ Discord nicht gefunden",
        "wizard.welcome.title": "Willkommen bei HandheldCord",
        "wizard.welcome.body": (
            "HandheldCord steuert deinen offiziellen Discord-Client mit dem Controller. Es greift nicht auf "
            "deinen Account zu und verändert Discord nicht – es drückt nur Tasten für dich.\n\n"
            "Die Einrichtung dauert etwa zwei Minuten. Für die Schritte in den Discord-Einstellungen darfst "
            "du einmalig den Touchscreen benutzen."
        ),
        "wizard.discord.title": "Discord starten",
        "wizard.discord.body": "Starte Discord und melde dich an. Ⓐ holt Discord nach vorne oder startet es.\n\n{status}",
        "wizard.discord.primary": "Discord öffnen",
        "wizard.mute.title": "Tastenkürzel für Mute",
        "wizard.mute.body": (
            "Damit Mute auch im Spiel funktioniert, braucht Discord ein globales Tastenkürzel:\n\n"
            "1. Öffne in Discord die Einstellungen → Tastenbelegungen (Keybinds).\n"
            "2. Füge eine Tastenbelegung mit der Aktion „Stummschaltung umschalten“ (Toggle Mute) hinzu.\n"
            "3. Tippe auf „Tastenbelegung aufnehmen“ und drücke Ⓐ – HandheldCord sendet {mute}.\n"
            "4. Beende die Aufnahme."
        ),
        "wizard.mute.primary": "{mute} senden",
        "wizard.deafen.title": "Tastenkürzel für Deafen",
        "wizard.deafen.body": (
            "Wie eben, nur mit der Aktion für Deafen (Toggle Deafen):\n\n"
            "1. Füge eine weitere Tastenbelegung hinzu.\n"
            "2. Starte die Aufnahme und drücke Ⓐ – HandheldCord sendet {deafen}.\n"
            "3. Beende die Aufnahme."
        ),
        "wizard.deafen.primary": "{deafen} senden",
        "wizard.ptt.title": "Push-to-Talk (optional)",
        "wizard.ptt.body": (
            "Wenn du Push-to-Talk nutzt: Lege eine Tastenbelegung mit der Aktion „Push to Talk (Normal)“ an, "
            "starte die Aufnahme und drücke Ⓐ – HandheldCord sendet {ptt}. Stelle danach unter "
            "Sprache & Video den Eingabemodus auf Push-to-Talk.\n\n"
            "Kein Push-to-Talk? Einfach mit RB weiter."
        ),
        "wizard.ptt.primary": "{ptt} senden",
        "wizard.test.title": "Testen",
        "wizard.test.body": (
            "Ⓐ löst Mute über {mute} aus, Ⓧ Deafen über {deafen}. In Discord sollte sich das Mikrofon- "
            "bzw. Kopfhörersymbol ändern.\n\n"
            "Passiert nichts? Geh mit Ⓑ zurück und nimm das Tastenkürzel neu auf."
        ),
        "wizard.test.primary": "Mute testen",
        "wizard.test.secondary": "Deafen testen",
        "wizard.buttons.title": "Tasten am Handheld",
        "wizard.buttons.body": (
            "Im Spiel gehört der Controller dem Spiel. Lege deshalb in Armoury Crate SE, Legion Space, "
            "MSI Center M oder Handheld Companion:\n\n"
            "• eine Zusatztaste auf {overlay} – sie wechselt zwischen Spiel und Discord,\n"
            "• eine Rückseitentaste auf {ptt} für Push-to-Talk,\n"
            "• bei Bedarf weitere Tasten auf {mute} (Mute) und {deafen} (Deafen).\n\n"
            "Keine freien Tasten? Halte ⧉ und ☰ eine halbe Sekunde gleichzeitig."
        ),
        "wizard.conflicts.title": "Doppelte Eingaben vermeiden",
        "wizard.conflicts.body": (
            "Wenn Steam oder Handheld Companion den Controller auf dem Desktop als Maus und Tastatur nutzen, "
            "kommt in Discord jede Eingabe doppelt an. Schalte diese Desktop-Steuerung für deinen Controller "
            "ab (in Steam: das Desktop-Layout), solange du HandheldCord verwendest."
        ),
        "wizard.done.title": "Fertig!",
        "wizard.done.body": (
            "Im Spiel: {overlay} oder ⧉ + ☰ halten → Discord.\n"
            "In Discord: ✛ Kanäle, LB/RB Server, Ⓨ schreiben, Ⓧ suchen, ☰ Menü, ⧉ Mute (lang: Deafen).\n\n"
            "Die Einrichtung findest du jederzeit im Menü (☰)."
        ),
        "wizard.done.primary": "Los geht's",
    },
}


def resolve_language(setting: str, system_locale: str) -> str:
    """"auto" follows the system locale; everything except German falls back to English."""
    if setting in STRINGS:
        return setting
    return "de" if system_locale.lower().startswith("de") else "en"


class Translator:
    def __init__(self, lang: str) -> None:
        self.lang = lang if lang in STRINGS else "en"

    def __call__(self, key: str, /, **params: object) -> str:
        text = STRINGS[self.lang].get(key) or STRINGS["en"].get(key) or key
        return text.format(**params) if params else text
