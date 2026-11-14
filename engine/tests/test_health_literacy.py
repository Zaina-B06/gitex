"""Task 05 Part D: every action has a plain-language variant and a fixed icon; reading_level and read_aloud exist."""

from rebound_engine.actions import ICONS, load_actions
from rebound_engine.models import Preferences, ReadingLevel


def test_every_action_has_an_icon_from_the_fixed_list():
    missing = [a.id for a in load_actions() if a.icon not in ICONS]
    assert not missing, f"no icon, or one not in ICONS: {missing}"


def test_every_action_has_a_simple_variant_in_both_languages():
    for a in load_actions():
        assert a.simple and a.simple.en.strip() and a.simple.ar.strip(), a.id
        # Real simpler Arabic, not a copy of the standard title.
        assert a.simple.ar != a.title.ar, a.id


def test_reading_level_and_read_aloud_default_off():
    p = Preferences()
    assert p.reading_level == ReadingLevel.standard and p.read_aloud is False
    assert Preferences(reading_level="simple", read_aloud=True).reading_level == ReadingLevel.simple
