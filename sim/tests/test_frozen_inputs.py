"""Task 05 Part B added behaviours, barriers and BCT codes to the engine. Personas must not see them, or every
persona's random draws would change and run_011 would no longer reproduce."""

from rebound_engine.actions import default_library
from rebound_engine.models import Behaviour
from sim.personas import BARRIERS, BCT_CODES


def test_persona_barriers_are_the_original_eight():
    assert BARRIERS == ["time", "energy_fatigue", "illness_pain", "schedule_change", "environment",
                        "low_motivation", "social_family", "forgot"]


def test_persona_bct_codes_come_from_movement_and_sleep_actions_only():
    codes = {a.bct_code for a in default_library() if a.behaviour in (Behaviour.movement, Behaviour.sleep)}
    assert BCT_CODES == sorted(codes)
