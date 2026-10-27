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


def test_view_mutes_with_the_handheld_mute_key(harness):
    harness.discord.in_front = True
    harness.tap("VIEW")
    assert harness.keys.calls == [("tap", "F6")]
    assert harness.ui.toasts == ["Mute toggled"]


def test_mute_in_a_game_uses_the_same_key(make_harness):
    h = make_harness(bindings={"game": [{"chord": ["L3", "R3"], "do": "voice.mute"}]})
    h.hold("L3", "R3")
    h.hold("L3", "R3", seconds=0.6)
    assert h.keys.calls == [("tap", "F6")]


def test_holding_x_lists_voice_channels(harness):
    harness.discord.in_front = True
    harness.hold("X")
    harness.hold("X", seconds=0.6)
    harness.hold()
    assert harness.keys.calls == [("tap", "Ctrl+K")]
    for _delay, callback in harness.scheduled:
        callback()
    assert harness.keys.calls == [("tap", "Ctrl+K"), ("type", "!")]
    harness.tap("DPAD_DOWN")
    harness.tap("A")  # Enter joins the selected voice channel
    assert harness.keys.calls[-2:] == [("tap", "Down"), ("tap", "Enter")]
    assert harness.router.stack == []


def test_tapping_x_still_opens_the_quick_switcher(harness):
    harness.discord.in_front = True
    harness.tap("X")
    assert harness.keys.calls == [("tap", "Ctrl+K")]
    assert harness.scheduled == []


def test_holding_b_asks_before_leaving_the_call(harness):
    harness.discord.in_front = True
    harness.hold("B")
    harness.hold("B", seconds=0.6)
    harness.hold()
    assert harness.ui.confirm["title"] == "Leave the call?"
    assert harness.keys.calls == []
    harness.tap("A")
    assert harness.keys.calls == [("tap", "Ctrl+Alt+Shift+F11")]
    assert harness.ui.confirm is None
    assert harness.router.stack == []


def test_answering_no_keeps_the_call(harness):
    harness.discord.in_front = True
    harness.hold("B")
    harness.hold("B", seconds=0.6)
    harness.hold()
    harness.tap("B")
    assert harness.keys.calls == []
    assert harness.ui.confirm is None


def test_tapping_b_is_still_escape(harness):
    harness.discord.in_front = True
    harness.tap("B")
    assert harness.keys.calls == [("tap", "Esc")]
    assert harness.ui.confirm is None


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


def go_to_step(harness, step_id):
    harness.router.open_wizard()
    while harness.router.wizard.step.id != step_id:
        harness.tap("RB")


def test_assistant_records_the_mute_key_in_discords_settings(harness):
    go_to_step(harness, "mute")
    assert harness.ui.wizard["title"] == "Mute key in Discord"
    harness.tap("A")  # Discord is not in front yet
    assert harness.keys.calls == []
    assert harness.ui.toasts[-1] == "Open Discord's settings first (Ⓧ)"
    harness.tap("X")
    assert harness.discord.in_front
    for _delay, callback in harness.scheduled:
        callback()
    assert harness.keys.calls == [("tap", "Ctrl+,")]
    harness.tap("A")
    assert harness.keys.calls[-1] == ("tap", "F6")
    assert harness.ui.toasts[-1] == "Sent F6"


def test_assistant_records_the_leave_keybind(harness):
    go_to_step(harness, "leave")
    harness.discord.in_front = True
    harness.tap("A")
    assert harness.keys.calls == [("tap", "Ctrl+Alt+Shift+F11")]


def test_key_picker_skips_keys_already_in_use(harness):
    go_to_step(harness, "mute")
    harness.tap("DPAD_RIGHT")  # F7 is push-to-talk, so the next free key is F8
    assert harness.cfg.handheld_keys["mute"] == "F8"
    assert harness.ui.wizard["key"]["label"] == "F8"
    assert json.loads(harness.cfg.path.read_text("utf-8"))["handheld_keys"]["mute"] == "F8"
    harness.tap("DPAD_LEFT")
    assert harness.cfg.handheld_keys["mute"] == "F6"


def test_changing_the_overlay_key_registers_it_again(harness):
    changes = []
    harness.router.on_keys_changed = lambda: changes.append(harness.cfg.handheld_keys["overlay"])
    go_to_step(harness, "overlay")
    harness.tap("DPAD_RIGHT")
    assert changes == ["F11"]


def test_overlay_key_is_detected_instead_of_switching(harness):
    go_to_step(harness, "overlay")
    harness.router.on_hotkey("overlay")
    assert harness.discord.calls == []
    assert harness.ui.toasts[-1] == "✔ F10 detected"


def test_assistant_can_collapse_and_move(harness):
    harness.router.open_wizard()
    assert harness.ui.wizard["position"] == "bottom-right"
    harness.tap("Y")
    assert harness.ui.wizard["collapsed"] is True
    harness.tap("Y")
    harness.tap("VIEW")
    assert harness.ui.wizard["collapsed"] is False
    assert harness.ui.wizard["position"] == "bottom-left"


def test_mute_test_leaves_discords_settings_first(harness):
    go_to_step(harness, "test")
    harness.discord.in_front = True
    harness.tap("A")
    assert harness.keys.calls == [("tap", "Esc")]
    for _delay, callback in harness.scheduled:
        callback()
    assert harness.keys.calls == [("tap", "Esc"), ("tap", "F6")]


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
    assert hints["Search (hold: Voice channels)"]["buttons"] == ["X"]
    assert hints["Back (hold: Leave call)"]["buttons"] == ["B"]
    assert hints["Game (hold)"] == {"buttons": ["VIEW", "MENU"], "label": "Game (hold)", "joiner": "+"}


def test_every_action_has_a_handler(harness):
    assert [action for action in sorted(SIMPLE_ACTIONS) if not harness.router.handles(action)] == []
