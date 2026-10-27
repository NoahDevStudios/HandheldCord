from handheldcord.input.gestures import Binding, ContextBindings, Fired, GestureEngine, Timing

TIMING = Timing(repeat_delay=0.4, repeat_interval=0.1, long_press=0.5, chord_hold=0.5)

VIEW_MENU = ContextBindings([
    Binding(("VIEW",), tap="mute", long="deafen"),
    Binding(("MENU",), press="menu"),
    Binding(("VIEW", "MENU"), press="toggle"),
])


def run(engine, ctx, steps):
    """steps: (time, pressed buttons); returns the fired actions."""
    fired = []
    for now, buttons in steps:
        for event in engine.update(frozenset(buttons), now, ctx):
            fired.append(event.action if event.phase == "fire" else f"{event.action}:{event.phase}")
    return fired


def test_press_fires_immediately_and_repeats():
    ctx = ContextBindings([Binding(("DPAD_UP",), press="up", repeat=True)])
    steps = [(0.0, {"DPAD_UP"}), (0.3, {"DPAD_UP"}), (0.41, {"DPAD_UP"}), (0.52, {"DPAD_UP"}), (0.6, set())]
    assert run(GestureEngine(TIMING), ctx, steps) == ["up", "up", "up"]


def test_tap_and_long_press():
    engine = GestureEngine(TIMING)
    assert run(engine, VIEW_MENU, [(0.0, {"VIEW"}), (0.2, set())]) == ["mute"]
    assert run(engine, VIEW_MENU, [(1.0, {"VIEW"}), (1.6, {"VIEW"}), (1.7, set())]) == ["deafen"]


def test_chord_fires_after_holding_and_swallows_the_single_buttons():
    steps = [
        (0.0, {"VIEW"}),
        (0.2, {"VIEW", "MENU"}),
        (0.6, {"VIEW", "MENU"}),  # VIEW is past its long press, but the chord is forming
        (0.75, {"VIEW", "MENU"}),
        (0.8, set()),
    ]
    assert run(GestureEngine(TIMING), VIEW_MENU, steps) == ["toggle"]


def test_aborted_chord_fires_nothing():
    assert run(GestureEngine(TIMING), VIEW_MENU, [(0.0, {"VIEW", "MENU"}), (0.2, set())]) == []


def test_chord_member_press_fires_on_release():
    assert run(GestureEngine(TIMING), VIEW_MENU, [(0.0, {"MENU"}), (0.1, set())]) == ["menu"]


def test_hold_emits_down_and_up():
    ctx = ContextBindings([Binding(("RB",), hold="ptt")])
    steps = [(0.0, {"RB"}), (0.5, {"RB"}), (0.6, set())]
    assert run(GestureEngine(TIMING), ctx, steps) == ["ptt:down", "ptt:up"]


def test_consume_all_keeps_held_buttons_inert_until_released():
    ctx = ContextBindings([Binding(("A",), press="ok")])
    engine = GestureEngine(TIMING)
    assert run(engine, ctx, [(0.0, {"A"})]) == ["ok"]
    assert engine.consume_all() == []
    assert run(engine, ctx, [(0.1, {"A"}), (0.2, set()), (0.3, {"A"})]) == ["ok"]


def test_consume_all_releases_active_holds():
    ctx = ContextBindings([Binding(("RB",), hold="ptt")])
    engine = GestureEngine(TIMING)
    run(engine, ctx, [(0.0, {"RB"})])
    assert engine.consume_all() == [Fired("ptt", "up")]
