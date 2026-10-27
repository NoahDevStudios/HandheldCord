# HandheldCord

Use Discord on Windows handhelds (ROG Ally, Legion Go, MSI Claw, …) with nothing but the controller.

> **Status:** early preview (v0.1, *companion mode*). Not affiliated with or endorsed by Discord Inc.

## What it does

HandheldCord sits next to the **official Discord desktop app** and makes it controller-friendly:

- Switch between your game and Discord with one button – or by holding **View + Menu**.
- Browse servers, channels and unread channels with the D-pad and bumpers.
- Type on a controller-optimized on-screen keyboard, or send quick replies from the quick menu.
- Join voice channels and leave calls without touching the screen.
- Mute and push-to-talk while you play, through Discord's own global keybinds.
- A hint bar always shows what each button does right now.

### Companion mode: no account access

HandheldCord does not talk to Discord's servers, never sees your login or token and does not modify the Discord app.
It only presses keyboard shortcuts for you – the same thing a Steam Input profile or a macro keypad does.

## Requirements

- Windows 10 or 11 with an XInput controller (every Windows handheld's built-in controller qualifies)
- The official Discord desktop app

## Install on your handheld

1. Open the [Releases page](../../releases) and download `HandheldCord-<version>-win64.zip`.
2. Extract it, for example to `Documents\HandheldCord`, and start `HandheldCord.exe`.
   The build is not signed yet, so Windows SmartScreen may warn: choose **More info → Run anyway**.
3. Optional – start with Windows: press <kbd>Win</kbd>+<kbd>R</kbd>, enter `shell:startup` and put a shortcut to `HandheldCord.exe` into the folder that opens.

No Python needed. To update, replace the folder with the new release; your settings live in `%APPDATA%\HandheldCord`.

## First start

A setup assistant opens in a corner of the screen – **Y** collapses it, **View** moves it to another corner, so Discord stays readable behind it.
It opens Discord's settings for you and records the keybinds HandheldCord needs; you only add the keybind and confirm with **A**.
All keys are standard keys (F1–F12 by default), so the app that came with your handheld can map buttons to them.
HandheldCord then lives in the system tray; reopen the assistant from the tray icon or the quick menu.

## Controls (defaults)

### In a game

The game owns the controller, so HandheldCord only listens for a few things:

| Input | Action |
|---|---|
| Hold **View + Menu** (0.5 s) | Bring Discord to the front |
| Spare button mapped to **F10** | Same – recommended (map it in Armoury Crate SE, Legion Space, MSI Center M or Handheld Companion) |
| Buttons mapped to **F6 / F7** | Mute / push-to-talk via Discord's global keybinds |

### In Discord

| Input | Action |
|---|---|
| D-pad ↑ ↓ / left stick | Previous / next channel |
| D-pad ← → | Previous / next unread channel |
| LB / RB | Previous / next server |
| LT / RT, right stick | Scroll the chat |
| A | Enter |
| B | Esc · **hold:** leave the call (asks first: A = yes, B = no) |
| X | Quick switcher (search channels, DMs, servers) · **hold:** voice channels |
| Y | On-screen keyboard |
| L3 | Emoji picker |
| Menu | Quick menu: quick replies, favorites, mute, join or leave voice, setup |
| View | Mute |
| Hold View + Menu | Back to the game |

Inside the quick switcher or emoji picker the D-pad sends plain arrow keys, **A** picks, **B** closes, **Y** opens the keyboard to type a search.
Discord's channel shortcuts skip voice channels, which is why holding **X** lists them – pick one and press **A** to join.

### On-screen keyboard

| Input | Action |
|---|---|
| D-pad / left stick | Move |
| A | Press key |
| X / Y | Backspace / space |
| LT / RT | Shift / symbols & emoji |
| LB / RB | Move the cursor |
| View | Insert the text into Discord |
| Menu | Send (insert + Enter) |
| B | Close (the text is kept) |

The keyboard never takes the focus, so the text lands in whatever Discord field is active. It also works with touch.

## Configuration

`%APPDATA%\HandheldCord\config.json` is created on first start. Edit it via the tray icon → *Open configuration*, then *Reload configuration*.

| Key | Meaning |
|---|---|
| `quick_replies` | Texts in the quick menu, e.g. `["gg", "brb", "👍"]` |
| `favorites` | `[{"name": "Squad – general", "query": "general"}]` – opens the quick switcher, types `query`, presses Enter |
| `handheld_keys` | Standard keys for your handheld buttons: `overlay` (switch game ⇄ Discord), `mute`, `ptt` – easiest to pick in the setup assistant (`""` turns one off) |
| `discord_shortcuts` | Discord's in-app shortcuts: `switcher`, `emoji`, `settings` |
| `discord_keybinds` | Keybinds that only HandheldCord sends: `disconnect` (leave the call) |
| `language` / `osk_layout` | `auto`, `en` or `de` |
| `maximize_discord` | Maximize Discord when bringing it to the front |
| `show_hints` | Show the button hint bar |
| `timing` | `repeat_delay_ms`, `repeat_interval_ms`, `long_press_ms`, `chord_hold_ms` |
| `bindings` | Per-context overrides of the controller layout (see below) |

### Custom bindings

Contexts: `game`, `discord`, `discord_popup`, `osk`, `menu`, `wizard`. A context listed under `bindings` replaces its defaults completely; `default-bindings.json` next to the config holds the defaults to copy from.

```json
"bindings": {
  "game": [
    {"chord": ["VIEW", "MENU"], "do": "overlay.toggle"},
    {"chord": ["L3", "R3"], "do": "voice.mute"}
  ]
}
```

- Entry forms: `{"on": "A", "do": …, "repeat": true}`, `{"on": "VIEW", "tap": …, "long": …}`, `{"on": "RB", "hold": "voice.ptt"}`, `{"chord": [...], "do": …}`
- Buttons: `A B X Y LB RB LT RT VIEW MENU L3 R3`, `DPAD_UP/DOWN/LEFT/RIGHT`, `LS_UP/…`, `RS_UP/…`
- Actions: `key:<combo>` (e.g. `key:Ctrl+K`), `text:<text>`, `reply:<n>`, `favorite:<n>`, `overlay.toggle`, `voice.mute`, `voice.ptt`, `voice.leave` (asks first), `voice.disconnect`, `discord.switcher`, `discord.voice_channels`, `discord.emoji`, `discord.settings`, `osk.open`, `menu.open`, `wizard.open`, plus the `osk.*`, `menu.*`, `popup.*`, `confirm.*` and `wizard.*` actions used by the defaults

## Known limitations

- **Double input:** if Steam Input's desktop layout or Handheld Companion's desktop mode turns the controller into mouse and keyboard, Discord gets every input twice. Turn that off while using HandheldCord.
- **Exclusive fullscreen** games are minimized when Discord comes to the front – borderless mode avoids that.
- HandheldCord doesn't read Discord's screen: the **mute state** isn't known (the toast only confirms the key was sent), and it can't tell whether a call is open – that's why leaving a call asks first.
- **Mute and push-to-talk keys reach the game as well.** Pick keys your game doesn't use (F5/F9 are often quicksave/quickload).
- If Discord runs **as administrator**, Windows blocks the simulated keys – run both at the same privilege level.
- Discord's shortcuts may change with updates; all of them are configurable.

## Development

Requires Python 3.11 or newer.

```powershell
git clone <repository-url> HandheldCord
cd HandheldCord
python -m venv .venv
.venv\Scripts\pip install -e .[dev]
.venv\Scripts\python -m pytest
.venv\Scripts\python -m handheldcord --dry-run --debug --debug-input
```

`--dry-run` logs key presses and window switches instead of performing them. The log is written to `%APPDATA%\HandheldCord\handheldcord.log`.

### Building and releasing

`pip install -e .[build]` and `python packaging/build.py` create `dist/HandheldCord-<version>-win64.zip` (PyInstaller, one folder, no Python required).
Releases are built by GitHub Actions: bump `__version__` in `src/handheldcord/__init__.py`, then push a matching tag such as `v0.1.0`.

## Roadmap

- Signed releases, an installer and a smaller build
- Xbox Game Bar widget
- Optional native lightweight client mode

## License

HandheldCord is free software under the [GNU General Public License v3.0 or later](LICENSE).

HandheldCord is an independent project. "Discord" is a trademark of Discord Inc.
