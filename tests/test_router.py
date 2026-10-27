import json

from handheldcord.companion.actions import SIMPLE_ACTIONS


def test_game_context_ignores_everything_but_the_chord(harness):
    harness.tap("A")
    harness.tap("DPAD_UP")
    assert harness.ui.context == "game"
    assert harness.keys.calls == []


def test_view_menu_chord_brings_discord_to_the_front(harness):
    harness.hold("VIEW", "MENU")
    harness.hold("VIEW", "MENU", seconds=0.6)
    assert harness.discord.calls == ["toggle", "show"]
    harness.hold("VIEW", "MENU")  # still held, now in the Discord context
    harness.hold()
    assert harness.ui.context == "discord"
    assert harness.ui.menu is None  # releasing MENU must not open the quick menu
    assert harness.keys.calls == []  # and releasing VIEW must not mute


def test_dpad_switches_channels_with_auto_repeat(harness):
    harness.discord.in_front = True
    harness.hold("DPAD_DOWN")
    harness.hold("DPAD_DOWN", seconds=0.3)
    harness.hold("DPAD_DOWN", seconds=0.15)
    assert harness.keys.calls == [("tap", "Alt+Down"), ("tap", "Alt+Down")]


def test_view_tap_mutes_and_long_press_deafens(harness):
    harness.discord.in_front = True
    harness.tap("VIEW")
    harness.hold("VIEW")
    harness.hold("VIEW", seconds=0.6)
    harness.hold()
    assert harness.keys.calls == [("tap", "Ctrl+Shift+M"), ("tap", "Ctrl+Shift+D")]
    assert harness.ui.toasts == ["Mute toggled", "Deafen toggled"]


def test_mute_in_a_game_uses_the_global_keybind(make_harness):
    h = make_harness(bindings={"game": [{"chord": ["L3", "R3"], "do": "voice.mute"}]})
    h.hold("L3", "R3")
    h.hold("L3", "R3", seconds=0.6)
    assert h.keys.calls == [("tap", "F13")]


def test_keyboard_types_and_sends(harness):
    harness.discord.in_front = True
    harness.tap("Y")
    assert harness.ui.osk is not None
    harness.tap("A")  # the highlighted key is "q"
    harness.tap("MENU")
    assert harness.keys.calls == [("type", "q"), ("tap", "Enter")]
    assert harness.ui.osk is None
    assert harness.router.stack == []


def test_keyboard_closes_when_discord_loses_the_focus(harness):
    harness.discord.in_front = True
    harness.tap("Y")
    harness.discord.in_front = False
    harness.hold()
    assert harness.ui.osk is None
    assert harness.ui.context == "game"


def test_quick_switcher_flow(harness):
    harness.discord.in_front = True
    harness.tap("X")
    harness.tap("DPAD_DOWN")
    harness.tap("A")
    assert harness.keys.calls == [("tap", "Ctrl+K"), ("tap", "Down"), ("tap", "Enter")]
    assert harness.router.stack == []


def test_quick_menu_sends_a_quick_reply(harness):
    harness.discord.in_front = True
    harness.tap("MENU")  # fires on release because MENU is part of the View+Menu chord
    assert harness.ui.menu["items"][0]["label"] == "gg"
    harness.tap("A")
    assert harness.keys.calls == [("type", "gg"), ("tap", "Enter")]
    assert harness.ui.menu is None


def test_favorites_go_through_the_quick_switcher(make_harness):
    h = make_harness(favorites=[{"name": "Squad", "query": "general"}])
    h.discord.in_front = True
    h.tap("MENU")
    labels = [item["label"] for item in h.ui.menu["items"]]
    for _ in range(labels.index("Squad")):
        h.tap("DPAD_DOWN")
    h.tap("A")
    assert h.keys.calls == [("tap", "Ctrl+K")]
    for _delay, callback in h.scheduled:
        callback()
    assert h.keys.calls == [("tap", "Ctrl+K"), ("type", "general"), ("tap", "Enter")]


def test_setup_assistant_sends_the_global_keybind(harness):
    harness.router.open_wizard()
    assert harness.ui.wizard["step"] == 0
    harness.tap("RB")
    harness.tap("RB")
    assert harness.ui.wizard["title"] == "Keybind for mute"
    harness.tap("A")
    assert harness.keys.calls == [("tap", "F13")]
    assert harness.ui.toasts[-1] == "Sent F13"


def test_closing_the_assistant_marks_setup_done(harness):
    harness.router.open_wizard()
    harness.tap("B")  # Back on the first step closes the assistant
    assert harness.ui.wizard is None
    assert json.loads(harness.cfg.path.read_text("utf-8"))["setup_done"] is True


def test_overlay_hotkey_toggles_discord(harness):
    harness.router.on_hotkey("overlay")
    assert harness.discord.calls == ["toggle", "show"]
    assert harness.discord.in_front


def test_started_discord_is_focused_once_its_window_exists(harness):
    harness.discord.running = False
    harness.router.on_hotkey("overlay")
    assert harness.ui.toasts == ["Starting Discord …"]
    harness.discord.running = True
    harness.hold(seconds=0.6)
    assert harness.discord.calls == ["toggle", "show", "show"]
    assert harness.discord.in_front


def test_hint_bar_lists_the_discord_controls(harness):
    harness.discord.in_front = True
    harness.hold()
    hints = {hint["label"]: hint for hint in harness.ui.hints}
    assert hints["Channel"]["buttons"] == ["DPAD_UP", "DPAD_DOWN"]
    assert hints["Mute (hold: Deafen)"]["buttons"] == ["VIEW"]
    assert hints["Game (hold)"] == {"buttons": ["VIEW", "MENU"], "label": "Game (hold)", "joiner": "+"}


def test_every_action_has_a_handler(harness):
    assert [action for action in sorted(SIMPLE_ACTIONS) if not harness.router.handles(action)] == []
