import pytest

from handheldcord.windows.keys import VK_CONTROL, VK_SHIFT, canonical, hotkey_modifiers, parse_combo
from handheldcord.windows.sender import utf16_units


def test_modifiers_come_out_in_canonical_order():
    combo = parse_combo("shift+ctrl+k")
    assert combo.modifiers == (VK_CONTROL, VK_SHIFT)
    assert combo.key == ord("K")
    assert str(combo) == "Ctrl+Shift+K"


def test_named_keys_and_aliases():
    assert parse_combo("F13").key == 0x7C
    assert canonical("pgdn") == "PageDown"
    assert canonical("Strg+Esc") == "Ctrl+Esc"
    assert parse_combo("Ctrl+,").key == 0xBC  # Discord: open user settings
    assert canonical("ctrl+comma") == "Ctrl+,"


@pytest.mark.parametrize("text", ["", "Ctrl+", "Hyper+K", "F25", "Ctrl+Shift"])
def test_invalid_combos_are_rejected(text):
    with pytest.raises(ValueError):
        parse_combo(text)


def test_hotkey_modifier_flags():
    assert hotkey_modifiers(parse_combo("Ctrl+Alt+Shift+F12")) == 0x1 | 0x2 | 0x4


def test_emoji_become_surrogate_pairs():
    assert utf16_units("a👍") == [0x61, 0xD83D, 0xDC4D]
