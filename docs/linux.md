# HandheldCord on Linux (Steam Input layout)

The HandheldCord app is Windows-only: Linux desktops (Wayland) and the Steam Deck's Game Mode don't let an app press keys in another app or bring windows to the front.
Steam Input can do the part that matters most, though. It gives the official Discord app the same controller layout that HandheldCord uses on Windows.

This works wherever Steam runs:

- **Linux handhelds:** Steam Deck, SteamOS and Bazzite devices, in Game Mode and in Desktop Mode
- **Linux PCs** with a controller and Steam

On Linux you don't install HandheldCord itself, just Discord and Steam.

> This layout hasn't been tested on every device yet. If something doesn't work, tell us in the [HandheldCord Discord](https://discord.gg/7mNGV3PtZ4).

## What you get

| | Windows app | Linux layout |
|---|---|---|
| Channels, unread channels, servers and scrolling with the controller | ✓ | ✓ |
| Hold X to list voice channels | ✓ | ✓ |
| Hold B to leave a call | ✓ (asks first) | ✓ (hold for 1 s instead) |
| Typing | HandheldCord's keyboard | Steam's on-screen keyboard |
| Mute and push-to-talk in games | ✓ | ✓ with spare buttons in your game's layout |
| Switch between game and Discord | one button | desktop: one button through a shortcut · Game Mode: STEAM menu |
| Hint bar, quick menu, quick replies | ✓ | – |

## 1. Install Discord and add it to Steam

1. Install the Discord app. On a Steam Deck, switch to Desktop Mode and install **Discord** from the Discover store. On a PC, use your distribution's package or the Flatpak.
2. In Steam on the desktop, choose **Games → Add a Non-Steam Game to My Library…**, tick **Discord** and add it.
3. From now on, start Discord through Steam: Steam only applies the layout to apps it started.

## 2. Build the layout

Open Steam's layout editor for Discord:

- **Game Mode:** Library → Non-Steam → Discord → controller icon → **Edit Layout**
- **Desktop or PC:** Steam → Library → right-click Discord → **Manage → Controller Layout**

Pick any template, then set the buttons like this. On a Steam Deck, keep the right trackpad as a mouse so you can still tap anything on screen.

| Button | Steam Input binding | In Discord |
|---|---|---|
| D-pad ↑ / ↓ | Left Alt + Up Arrow / Left Alt + Down Arrow | Previous / next channel |
| D-pad ← / → | Left Alt + Left Shift + Up Arrow / Left Alt + Left Shift + Down Arrow | Previous / next unread channel |
| LB / RB | Left Ctrl + Left Alt + Up Arrow / Left Ctrl + Left Alt + Down Arrow | Previous / next server |
| LT / RT | Page Up / Page Down | Scroll the chat |
| Right joystick | Mode **Scroll Wheel** | Scroll the chat |
| A | Enter | Confirm, send |
| B | Tap: Escape · Hold (1 s): Left Ctrl + Left Alt + Left Shift + F11 | Back · leave the call |
| X | Tap: Left Ctrl + K · Hold: Left Ctrl + K, then Left Shift + 1 | Quick switcher · voice channels |
| Y | System → **Show Keyboard** | Steam's on-screen keyboard |
| Left joystick click | Left Ctrl + E | Emoji picker |
| View | F6 | Mute |
| Menu | Left Alt + Tab | Back to the game (desktop sessions) |
| A spare button, e.g. a back button | F7 | Push-to-talk (optional) |

**Key combinations:** pick the first key, then use **Add extra command** for every further key on the same activator.

**Tap and hold on B and X:**

1. The tap is a **Regular Press**. In its activator settings, turn **Interruptible** on: the tap then only fires if you let go before the long press.
2. Add an activator of the type **Long Press** with the hold keys. On B, set **Long Press Time** to 1000 ms so leaving a call needs a deliberate hold.
3. On X only: add a second **Long Press** activator with Left Shift + 1 (that's "!") and a **Fire Start Delay** of 200 ms. After "!", Discord's quick switcher lists only voice channels: pick one with the D-pad and press A to join. If the "!" goes missing, raise the delay.

Optional: set the left joystick to the mode **Directional Pad** with the same bindings as the D-pad.

## 3. Record the keybinds in Discord

Same as on Windows: Discord → User Settings → **Keybinds** → **Add a Keybind**, choose the action, select **Record Keybind**, press the button, then stop recording.

| Action in Discord | Press | Discord records |
|---|---|---|
| Toggle Mute | View | F6 |
| Push to Talk (Normal), optional | your push-to-talk button | F7 |
| Disconnect (leave voice) | hold B for 1 s | Ctrl+Alt+Shift+F11 |

## 4. Switch between game and Discord

Leave Discord running in the background.

**Game Mode (Steam Deck and other SteamOS handhelds):** press **STEAM**. Discord is listed at the top with the running apps; pick it. Go back to your game the same way.

**Desktop sessions (Steam Deck Desktop Mode, Bazzite desktop, Linux PCs):**

1. Create a system shortcut that opens Discord, for example Meta+D. Discord only runs once, so the shortcut brings the open window to the front.
   - KDE Plasma: System Settings → Keyboard → Shortcuts → **Add New** → Application → Discord
   - GNOME: Settings → Keyboard → **Custom Shortcuts**, command `flatpak run com.discordapp.Discord` (or `discord` for the distribution package)
2. Put that shortcut on a spare button of your game's layout, such as a Steam Deck back button. On a PC you can set it once for every game in Steam's **Guide Button Chord Layout** (Steam Settings → Controller).
3. In Discord, **Menu** (Alt+Tab) takes you back to the game.

## 5. Mute and push-to-talk while playing

While a game is in front, Steam uses that game's layout, not the Discord layout. Add **F6** (mute) and **F7** (push-to-talk) to spare buttons there; the Steam Deck's back buttons are ideal. On a PC you can set them once in the Guide Button Chord Layout instead.

Pick keys your game doesn't use. F5 and F9 are often quicksave and quickload, so the defaults stay away from them.

On KDE Plasma with Wayland, Discord only hears keys typed into other apps if you allow it: search System Settings for **Legacy X11 App Support** and let X11 apps read all keystrokes.

Not tested yet: whether Discord receives these keys in the Steam Deck's Game Mode while a game is in front.

## Cheat sheet

| In Discord | |
|---|---|
| D-pad ↑ ↓ | channels |
| D-pad ← → | unread channels |
| LB / RB | servers |
| LT / RT, right joystick | scroll |
| A / B | confirm / back |
| Hold B (1 s) | leave the call |
| X / hold X | search / voice channels |
| Y | keyboard |
| Left joystick click | emoji |
| View | mute |
| Menu | back to the game (desktop) |
