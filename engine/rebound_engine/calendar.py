"""Context the engine works out by itself (Task 05 Part A2): Ramadan, Eid, heat and real shift timings.

Used only when an Engine is given a calendar (the API does; the simulator doesn't, so its results are unchanged).
Offline tables, no network calls."""

from datetime import date, time, timedelta
from typing import Protocol

from . import config
from .models import ContextFlag, DayContext, DayTimes, UserProfile, Weekday

# (1 Ramadan, 1 Shawwal = Eid al-Fitr) from the pre-computed Umm al-Qura calendar:
# R.H. van Gent, "The Principal Islamic Days of Observance according to the Umm al-Qura Calendar", Utrecht University,
# https://webspace.science.uu.nl/~gent0113/islam/ummalqura_principal.htm
# Moon-sighting (as used in the UAE) can shift either date by about a day; the user's "Ramadan started today / ended"
# tap corrects it (start_shift / end_shift below).
RAMADAN: tuple[tuple[date, date], ...] = (
    (date(2026, 2, 18), date(2026, 3, 20)),  # 1447
    (date(2027, 2, 8), date(2027, 3, 9)),  # 1448
    (date(2028, 1, 28), date(2028, 2, 26)),  # 1449
)

# Abu Dhabi (24.4539 N, 54.3773 E, UTC+4) on the 15th of each month: (dawn = Fajr / end of suhoor, sun 18.2 degrees
# below the horizon as used for UAE Fajr; sunset = iftar, sun -0.833 degrees). Computed offline with the NOAA
# solar-position equations (J. Meeus, Astronomical Algorithms), not read from an official timetable: within a few
# minutes across each month. Users can set their own iftar time. Only the months Ramadan falls in for 2026-2028;
# extend for 2029 onwards (Ramadan moves about 11 days earlier each year).
DAWN_SUNSET: dict[int, tuple[time, time]] = {
    1: (time(5, 47), time(17, 55)),
    2: (time(5, 39), time(18, 17)),
    3: (time(5, 15), time(18, 31)),
}

_WEEKDAYS = list(Weekday)  # date.weekday(): Monday = 0


class Calendar(Protocol):
    def day(self, profile: UserProfile, day: int) -> DayContext: ...


def day_context(profile: UserProfile, d: date, start_shift: int = 0, end_shift: int = 0) -> DayContext:
    flags: set[ContextFlag] = set()
    iftar: int | None = None
    if d.month in config.HEAT_MONTHS:
        flags.add(ContextFlag.heat)
    if profile.preferences.fasting_ramadan:
        for start, shawwal in RAMADAN:
            begins, ends = start + timedelta(days=start_shift), shawwal + timedelta(days=end_shift)
            if begins <= d < ends:
                flags.add(ContextFlag.ramadan)
                t = profile.preferences.iftar_time or DAWN_SUNSET.get(d.month, (None, None))[1]
                iftar = t.hour if t else None
            elif ends <= d < ends + timedelta(days=config.EID_REST_DAYS):
                flags.add(ContextFlag.eid)
    return DayContext(local_date=d, flags=flags, iftar_hour=iftar, day_times=shift_times(profile, d))


def _end_hour(t: time) -> int:
    return t.hour + (1 if t.minute else 0)  # a shift ending 06:30 keeps the 06:00 hour busy


def shift_times(profile: UserProfile, d: date) -> DayTimes | None:
    """Today's wake/sleep and busy hours from the weekly shift pattern; None if the user gave no shifts."""
    shifts = profile.basics.shifts
    if not shifts:
        return None
    today, yesterday = _WEEKDAYS[d.weekday()], _WEEKDAYS[(d.weekday() - 1) % 7]
    busy: list[tuple[int, int]] = []
    night_end: int | None = None
    for s in shifts:
        overnight = s.end <= s.start
        if today in s.days:
            busy.append((s.start.hour, 24 if overnight else _end_hour(s.end)))
        if overnight and yesterday in s.days and _end_hour(s.end) > 0:
            busy.append((0, _end_hour(s.end)))
            if s.end.hour < config.NIGHT_SHIFT_ENDS_BEFORE_H:
                night_end = _end_hour(s.end)
    if night_end is None:
        b = profile.basics
        return DayTimes(wake=b.usual_wake_time.hour, sleep=b.usual_sleep_time.hour, busy=busy)
    sleep = night_end + config.SHIFT_HOME_H
    wake = sleep + config.SHIFT_SLEEP_H
    busy.append((sleep % 24, wake % 24) if wake < 24 else (sleep % 24, 24))
    if wake >= 24:
        busy.append((0, wake - 24))
    return DayTimes(wake=wake % 24, sleep=sleep % 24, sleep_prompt=night_end % 24, busy=busy)


def in_busy(hour: int, ranges: list[tuple[int, int]]) -> bool:
    return any(s <= hour < e if s <= e else (hour >= s or hour < e) for s, e in ranges)
