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
        "hint.voice_channels": "Voice channels",
        "hint.emoji": "Emoji",
        "hint.settings": "Settings",
        "hint.write": "Write",
        "hint.menu": "Menu",
        "hint.mute": "Mute",
        "hint.ptt": "Push-to-talk",
        "hint.leave": "Leave call",
        "hint.yes": "Yes",
        "hint.no": "No",
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
        "toast.sent": "Sent {key}",
        "toast.key_detected": "✔ {key} detected",
        "toast.discord_first": "Open Discord's settings first (Ⓧ)",
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
        "menu.voice_channels": "Join a voice channel",
        "menu.leave": "Leave the call",
        "menu.to_game": "Back to the game",
        "menu.setup": "Open setup",
        "confirm.yes": "Yes",
        "confirm.no": "No",
        "confirm.leave.title": "Leave the call?",
        "confirm.leave.body": "You will be disconnected from voice.",
        "tray.tooltip": "HandheldCord – companion mode",
        "tray.setup": "Setup …",
        "tray.config": "Open configuration",
        "tray.reload": "Reload configuration",
        "tray.quit": "Quit",
        "wizard.next": "Next",
        "wizard.back": "Back",
        "wizard.close": "Close",
        "wizard.record": "Send {key}",
        "wizard.open_settings": "Open settings",
        "wizard.key": "Key",
        "wizard.collapse": "Collapse",
        "wizard.expand": "Show setup",
        "wizard.move": "Move",
        "wizard.status.found": "✔ Discord found",
        "wizard.status.missing": "✖ Discord not found",
        "wizard.welcome.title": "Welcome to HandheldCord",
        "wizard.welcome.body": (
            "HandheldCord controls your official Discord app with your controller. It never touches your "
            "account and doesn't modify Discord – it only presses keys for you.\n\n"
            "Collapse this window with Ⓨ or move it to another corner with ⧉ to see what Discord shows behind it."
        ),
        "wizard.discord.title": "Start Discord",
        "wizard.discord.body": "Start Discord and log in. Ⓐ brings Discord to the front or starts it.\n\n{status}",
        "wizard.discord.primary": "Open Discord",
        "wizard.overlay.title": "Key for Discord ⇄ game",
        "wizard.overlay.body": (
            "This key brings Discord to the front and takes you back to your game. Pick it with ◀ ▶ – "
            "you will map it to a spare handheld button in a moment.\n\n"
            "Press it now to test it: HandheldCord shows “detected”. Without a spare button, "
            "holding ⧉ + ☰ works too."
        ),
        "wizard.mute.title": "Mute key in Discord",
        "wizard.mute.body": (
            "Pick with ◀ ▶ the key you will map to your mute button.\n\n"
            "1. Ⓧ opens Discord's settings – tap “Keybinds” on the left.\n"
            "2. “Add a Keybind”, choose the action “Toggle Mute” and tap “Record Keybind”.\n"
            "3. Press Ⓐ – HandheldCord sends {mute}. Then stop recording."
        ),
        "wizard.ptt.title": "Push-to-talk (optional)",
        "wizard.ptt.body": (
            "Same as before with the action “Push to Talk (Normal)”: pick the key with ◀ ▶, add a keybind, "
            "start recording and Ⓐ sends {ptt}. Then switch the input mode to Push to Talk under "
            "“Voice & Video”.\n\n"
            "No push-to-talk? Just continue with RB."
        ),
        "wizard.leave.title": "Leaving a call",
        "wizard.leave.body": (
            "Discord has no fixed shortcut for leaving a call, only a keybind action. HandheldCord uses it "
            "when you hold Ⓑ in Discord – after asking first.\n\n"
            "Add a keybind with the action for disconnecting from voice, start recording and Ⓐ sends {leave}. "
            "This key does not need a handheld button."
        ),
        "wizard.test.title": "Test",
        "wizard.test.body": (
            "Discord turns its keybinds off while the Keybinds page is open. So Ⓐ first closes the settings, "
            "then triggers mute via {mute} – the microphone in Discord should be crossed out.\n\n"
            "Nothing happens? Go back with Ⓑ and record the key again."
        ),
        "wizard.test.primary": "Test mute",
        "wizard.buttons.title": "Map your handheld buttons",
        "wizard.buttons.body": (
            "Now map spare buttons in your handheld app (Armoury Crate SE, Legion Space, MSI Center M or "
            "Handheld Companion) to these keys:\n\n"
            "• {overlay} – Discord ⇄ game\n"
            "• {mute} – mute\n"
            "• {ptt} – push-to-talk (hold)\n\n"
            "Mute and push-to-talk reach the game too, so avoid keys your game uses – F5 and F9 are often "
            "quicksave and quickload."
        ),
        "wizard.conflicts.title": "Avoid double input",
        "wizard.conflicts.body": (
            "If Steam or Handheld Companion use your controller as mouse and keyboard on the desktop, "
            "Discord receives every input twice. Turn that desktop control off for your controller "
            "(in Steam: the desktop layout) while you use HandheldCord."
        ),
        "wizard.done.title": "All set!",
        "wizard.done.body": (
            "In a game: {overlay} or hold ⧉ + ☰ → Discord. {mute} mutes, {ptt} is push-to-talk.\n"
            "In Discord: ✛ channels, LB/RB servers, Ⓧ search (hold: voice channels), Ⓑ back "
            "(hold: leave call), Ⓨ write, ☰ menu, ⧉ mute.\n\n"
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
        "hint.voice_channels": "Sprachkanäle",
        "hint.emoji": "Emoji",
        "hint.settings": "Einstellungen",
        "hint.write": "Schreiben",
        "hint.menu": "Menü",
        "hint.mute": "Mute",
        "hint.ptt": "Push-to-Talk",
        "hint.leave": "Call verlassen",
        "hint.yes": "Ja",
        "hint.no": "Nein",
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
        "toast.sent": "{key} gesendet",
        "toast.key_detected": "✔ {key} erkannt",
        "toast.discord_first": "Öffne zuerst die Discord-Einstellungen (Ⓧ)",
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
        "menu.voice_channels": "Sprachkanal beitreten",
        "menu.leave": "Call verlassen",
        "menu.to_game": "Zurück zum Spiel",
        "menu.setup": "Einrichtung öffnen",
        "confirm.yes": "Ja",
        "confirm.no": "Nein",
        "confirm.leave.title": "Call verlassen?",
        "confirm.leave.body": "Du wirst vom Sprachkanal getrennt.",
        "tray.tooltip": "HandheldCord – Begleitmodus",
        "tray.setup": "Einrichtung …",
        "tray.config": "Konfiguration öffnen",
        "tray.reload": "Konfiguration neu laden",
        "tray.quit": "Beenden",
        "wizard.next": "Weiter",
        "wizard.back": "Zurück",
        "wizard.close": "Schließen",
        "wizard.record": "{key} senden",
        "wizard.open_settings": "Einstellungen öffnen",
        "wizard.key": "Taste",
        "wizard.collapse": "Einklappen",
        "wizard.expand": "Einrichtung anzeigen",
        "wizard.move": "Verschieben",
        "wizard.status.found": "✔ Discord gefunden",
        "wizard.status.missing": "✖ Discord nicht gefunden",
        "wizard.welcome.title": "Willkommen bei HandheldCord",
        "wizard.welcome.body": (
            "HandheldCord steuert deinen offiziellen Discord-Client mit dem Controller. Es greift nicht auf "
            "deinen Account zu und verändert Discord nicht – es drückt nur Tasten für dich.\n\n"
            "Dieses Fenster klappst du mit Ⓨ ein und schiebst es mit ⧉ in eine andere Ecke, damit du siehst, "
            "was Discord dahinter anzeigt."
        ),
        "wizard.discord.title": "Discord starten",
        "wizard.discord.body": "Starte Discord und melde dich an. Ⓐ holt Discord nach vorne oder startet es.\n\n{status}",
        "wizard.discord.primary": "Discord öffnen",
        "wizard.overlay.title": "Taste für Discord ⇄ Spiel",
        "wizard.overlay.body": (
            "Diese Taste holt Discord nach vorne und bringt dich zurück ins Spiel. Wähle sie mit ◀ ▶ – "
            "gleich legst du sie in deiner Handheld-App auf einen freien Knopf.\n\n"
            "Drück sie jetzt zum Testen: HandheldCord meldet „erkannt“. Ohne freien Knopf geht es auch mit "
            "⧉ + ☰ (halten)."
        ),
        "wizard.mute.title": "Mute-Taste in Discord",
        "wizard.mute.body": (
            "Wähle mit ◀ ▶ die Taste, die du auf deinen Mute-Knopf legst.\n\n"
            "1. Ⓧ öffnet die Discord-Einstellungen – tippe links auf „Tastenbelegungen“ (Keybinds).\n"
            "2. „Tastenbelegung hinzufügen“, Aktion „Stummschaltung umschalten“ (Toggle Mute) wählen und "
            "„Tastenbelegung aufnehmen“ antippen.\n"
            "3. Ⓐ drücken – HandheldCord sendet {mute}. Danach die Aufnahme beenden."
        ),
        "wizard.ptt.title": "Push-to-Talk (optional)",
        "wizard.ptt.body": (
            "Wie eben, mit der Aktion „Push to Talk (Normal)“: Taste mit ◀ ▶ wählen, Tastenbelegung "
            "hinzufügen, Aufnahme starten, Ⓐ sendet {ptt}. Stelle danach unter „Sprache & Video“ den "
            "Eingabemodus auf Push-to-Talk.\n\n"
            "Kein Push-to-Talk? Einfach mit RB weiter."
        ),
        "wizard.leave.title": "Call verlassen",
        "wizard.leave.body": (
            "Discord hat kein festes Kürzel zum Verlassen eines Calls, aber eine Aktion für Tastenbelegungen. "
            "HandheldCord nutzt sie, wenn du in Discord Ⓑ gedrückt hältst – nach einer Rückfrage.\n\n"
            "Tastenbelegung hinzufügen, die Aktion zum Trennen vom Sprachkanal wählen, Aufnahme starten – "
            "Ⓐ sendet {leave}. Diese Taste musst du nicht am Handheld belegen."
        ),
        "wizard.test.title": "Testen",
        "wizard.test.body": (
            "Solange die Seite „Tastenbelegungen“ offen ist, schaltet Discord seine Tastenkürzel ab. Ⓐ schließt "
            "deshalb zuerst die Einstellungen und löst dann Mute über {mute} aus – das Mikrofon in Discord "
            "sollte durchgestrichen sein.\n\n"
            "Passiert nichts? Geh mit Ⓑ zurück und nimm die Taste neu auf."
        ),
        "wizard.test.primary": "Mute testen",
        "wizard.buttons.title": "Knöpfe am Handheld belegen",
        "wizard.buttons.body": (
            "Lege jetzt in deiner Handheld-App (Armoury Crate SE, Legion Space, MSI Center M oder Handheld "
            "Companion) freie Knöpfe auf diese Tasten:\n\n"
            "• {overlay} – Discord ⇄ Spiel\n"
            "• {mute} – Mute\n"
            "• {ptt} – Push-to-Talk (halten)\n\n"
            "Mute und Push-to-Talk kommen auch im Spiel an. Nimm daher keine Tasten, die dein Spiel nutzt – "
            "F5 und F9 sind oft Schnellspeichern und -laden."
        ),
        "wizard.conflicts.title": "Doppelte Eingaben vermeiden",
        "wizard.conflicts.body": (
            "Wenn Steam oder Handheld Companion den Controller auf dem Desktop als Maus und Tastatur nutzen, "
            "kommt in Discord jede Eingabe doppelt an. Schalte diese Desktop-Steuerung für deinen Controller "
            "ab (in Steam: das Desktop-Layout), solange du HandheldCord verwendest."
        ),
        "wizard.done.title": "Fertig!",
        "wizard.done.body": (
            "Im Spiel: {overlay} oder ⧉ + ☰ halten → Discord. {mute} schaltet stumm, {ptt} ist Push-to-Talk.\n"
            "In Discord: ✛ Kanäle, LB/RB Server, Ⓧ suchen (halten: Sprachkanäle), Ⓑ zurück "
            "(halten: Call verlassen), Ⓨ schreiben, ☰ Menü, ⧉ Mute.\n\n"
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
