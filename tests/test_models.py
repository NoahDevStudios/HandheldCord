import json

from handheldcord import config
from handheldcord.companion.hints import LABELS
from handheldcord.companion.osk import OskModel
from handheldcord.companion.wizard import STEPS
from handheldcord.i18n import STRINGS, Translator, resolve_language


def test_osk_types_with_one_shot_shift():
    osk = OskModel("de")
    assert osk.current.value == "q"
    osk.toggle_shift()
    osk.press()
    osk.move(0, 1)
    osk.press()
    assert osk.text == "Qw"


def test_osk_backspace_removes_a_whole_heart():
    osk = OskModel()
    osk.insert("hi❤️")
    osk.backspace()
    assert osk.text == "hi"


def test_osk_vertical_moves_keep_the_horizontal_position():
    osk = OskModel("en")
    osk.select(4, 1)  # the wide space bar
    osk.move(-1, 0)
    assert osk.current.value in "xcv"


def test_osk_symbol_layer_and_commit_keys():
    osk = OskModel("en", {"send": "Send"})
    osk.toggle_symbols()
    assert osk.rows[3][0].value == "👍"
    osk.select(4, 4)
    assert osk.press() == "send"
    assert osk.snapshot()["rows"][4][4]["label"] == "Send"


def test_first_start_writes_the_defaults(tmp_path):
    cfg = config.load(tmp_path / "config.json")
    assert (tmp_path / "config.json").exists()
    assert cfg.handheld_keys == {"overlay": "F10", "mute": "F6", "ptt": "F7"}
    assert cfg.discord_shortcuts["settings"] == "Ctrl+,"
    assert not cfg.setup_done


def test_user_values_are_merged_and_validated(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({
        "config_version": 2,
        "handheld_keys": {"mute": "f8", "ptt": "Hyper+X", "overlay": ""},
        "quick_replies": ["hi", 5, " "],
        "bindings": {"game": []},
    }), "utf-8")
    cfg = config.load(path)
    assert cfg.handheld_keys == {"overlay": "", "mute": "F8", "ptt": "F7"}
    assert cfg.quick_replies == ["hi"]
    assert cfg.bindings["game"] == []
    assert cfg.bindings["discord"]  # contexts not listed keep their defaults


def test_version_1_config_is_migrated_to_standard_keys(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({
        "global_keybinds": {"mute": "F13", "deafen": "F14", "ptt": "F15"},
        "overlay_hotkey": "Ctrl+Alt+Shift+F12",
        "discord_shortcuts": {"mute": "Ctrl+Shift+M", "deafen": "Ctrl+Shift+D", "switcher": "Ctrl+K"},
        "quick_replies": ["hi"],
        "setup_done": True,
    }), "utf-8")
    cfg = config.load(path)
    assert cfg.handheld_keys == {"overlay": "F10", "mute": "F6", "ptt": "F7"}
    assert not cfg.setup_done  # Discord's keybinds have to be recorded again
    saved = json.loads(path.read_text("utf-8"))
    assert saved["config_version"] == 2
    assert "global_keybinds" not in saved and "overlay_hotkey" not in saved
    assert "mute" not in saved["discord_shortcuts"]
    assert saved["quick_replies"] == ["hi"]


def test_broken_config_is_never_overwritten(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("{ not json", "utf-8")
    cfg = config.load(path)
    assert cfg.error
    cfg.mark_setup_done()
    assert path.read_text("utf-8") == "{ not json"


def test_config_with_bom_is_accepted(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('﻿{"language": "de"}', "utf-8")
    assert config.load(path).language == "de"


def test_languages_have_the_same_keys():
    assert set(STRINGS["en"]) == set(STRINGS["de"])


def test_every_referenced_string_exists():
    keys = set(STRINGS["en"])
    for step in STEPS:
        assert {f"wizard.{step.id}.title", f"wizard.{step.id}.body"} <= keys
        if step.primary and step.primary != "record":
            assert f"wizard.{step.id}.primary" in keys
    assert set(LABELS.values()) <= keys


def test_wizard_texts_format_in_both_languages():
    params = {"overlay": "F10", "mute": "F6", "ptt": "F7", "leave": "Ctrl+Alt+Shift+F11", "status": "ok"}
    for lang in STRINGS:
        t = Translator(lang)
        for step in STEPS:
            assert "{" not in t(f"wizard.{step.id}.body", **params)


def test_language_resolution():
    assert resolve_language("auto", "de_AT") == "de"
    assert resolve_language("auto", "fr_FR") == "en"
    assert resolve_language("en", "de_DE") == "en"
