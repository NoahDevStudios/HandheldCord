import pytest

from handheldcord.companion.actions import DEFAULT_BINDINGS, normalize_action
from handheldcord.input.buttons import XINPUT_BITS, PadState
from handheldcord.input.normalize import Normalizer
from handheldcord.input.profile import load_profile, parse_binding


def test_pads_are_merged_without_doubling():
    physical = PadState(buttons=XINPUT_BITS["A"])
    virtual = PadState(buttons=XINPUT_BITS["A"] | XINPUT_BITS["B"])
    assert Normalizer().update([physical, virtual]) == {"A", "B"}


def test_trigger_hysteresis():
    normalizer = Normalizer()
    assert "LT" not in normalizer.update([PadState(lt=0.45)])
    assert "LT" in normalizer.update([PadState(lt=0.55)])
    assert "LT" in normalizer.update([PadState(lt=0.35)])  # still above the release threshold
    assert "LT" not in normalizer.update([PadState(lt=0.2)])


def test_stick_uses_the_dominant_axis():
    normalizer = Normalizer()
    assert normalizer.update([PadState(lx=0.7, ly=0.65)]) == {"LS_RIGHT"}
    assert normalizer.update([PadState(lx=0.45, ly=0.8)]) == {"LS_RIGHT"}  # held direction wins
    assert normalizer.update([PadState(lx=0.1, ly=0.8)]) == {"LS_UP"}
    assert normalizer.update([PadState()]) == frozenset()


def test_default_bindings_are_valid(caplog):
    profile = load_profile(DEFAULT_BINDINGS, normalize_action)
    assert "Ignoring" not in caplog.text
    assert set(profile) == set(DEFAULT_BINDINGS)
    assert profile["discord"].singles["DPAD_UP"].press == "key:Alt+Up"


def test_aliases_and_key_normalisation():
    binding = parse_binding({"on": "start", "do": "key:ctrl+alt+up"}, normalize_action)
    assert binding.buttons == ("MENU",)
    assert binding.press == "key:Ctrl+Alt+Up"


def test_do_together_with_long_becomes_a_tap():
    binding = parse_binding({"on": "A", "do": "voice.mute", "long": "voice.deafen"}, normalize_action)
    assert (binding.press, binding.tap, binding.long) == (None, "voice.mute", "voice.deafen")


def test_invalid_bindings_are_skipped(caplog):
    entries = [
        {"on": "Z", "do": "key:Enter"},
        {"on": "A", "do": "explode"},
        {"chord": ["A"], "do": "osk.open"},
        {"on": "B", "do": "key:Esc"},
    ]
    profile = load_profile({"discord": entries}, normalize_action)
    assert list(profile["discord"].singles) == ["B"]
    assert caplog.text.count("Ignoring") == 3


def test_indexed_actions():
    assert normalize_action("reply:2") == "reply:2"
    with pytest.raises(ValueError):
        normalize_action("reply:x")
