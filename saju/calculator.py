"""사주 계산 오케스트레이션 + 음/양력 입력 처리."""

from __future__ import annotations

from datetime import datetime

from korean_lunar_calendar import KoreanLunarCalendar

from .gapja import EARTHLY_BRANCHES, HEAVENLY_STEMS
from .luck import daewoon_pillars, seun_pillars
from .pillars import (
    day_pillar,
    hour_pillar,
    month_pillar,
    year_pillar,
)
from .tables import count_elements, hidden_stems, nayin_of


def _enrich(p: dict | None) -> dict | None:
    """4주 간지에 지장간·납음오행을 덧붙인다."""
    if p is None:
        return None
    stem_idx = HEAVENLY_STEMS.index(p["stem"])
    branch_idx = EARTHLY_BRANCHES.index(p["branch"])
    return {
        **p,
        "hidden_stems": hidden_stems(p["branch"]),
        "nayin": nayin_of(stem_idx, branch_idx),
    }


def lunar_to_solar(year: int, month: int, day: int, is_leap_month: bool = False) -> datetime:
    """음력 → 양력 datetime(00:00). 유효하지 않으면 ValueError."""
    cal = KoreanLunarCalendar()
    if not cal.setLunarDate(year, month, day, is_leap_month):
        raise ValueError("유효하지 않은 음력 날짜입니다.")
    iso = cal.SolarIsoFormat()  # 'YYYY-MM-DD'
    return datetime.strptime(iso, "%Y-%m-%d")


def calculate_saju(
    year: int,
    month: int,
    day: int,
    hour: int | None = None,
    *,
    is_lunar: bool = False,
    is_leap_month: bool = False,
    gender: str | None = None,
) -> dict:
    """생년월일시로 사주 4주와 부가 정보를 계산.

    - is_lunar=True면 입력을 음력으로 보고 양력으로 변환 후 계산.
    - hour(0~23)가 None이면 시주는 생략(시간 모름).
    - gender('male'|'female')가 주어지면 대운(순행/역행, 대운수, 대운 리스트)도 계산.
      gender가 없으면 daewoon은 None.
    반환: {'solar', 'lunar', 'pillars', 'elements', 'daewoon', 'seun'}
    """
    if is_lunar:
        solar_dt = lunar_to_solar(year, month, day, is_leap_month)
    else:
        try:
            solar_dt = datetime(year, month, day)
        except ValueError as exc:
            raise ValueError("유효하지 않은 양력 날짜입니다.") from exc

    birth_hour = hour if hour is not None else 0
    dt = solar_dt.replace(hour=birth_hour)

    yp = year_pillar(dt)
    year_stem_idx = HEAVENLY_STEMS.index(yp["stem"])
    mp = month_pillar(dt, year_stem_idx)
    dp, day_stem_idx = day_pillar(dt)

    pillars = {"year": yp, "month": mp, "day": dp}
    pillars["hour"] = hour_pillar(day_stem_idx, hour) if hour is not None else None

    elements = count_elements(pillars)

    daewoon = None
    if gender is not None:
        month_stem_idx = HEAVENLY_STEMS.index(mp["stem"])
        month_branch_idx = EARTHLY_BRANCHES.index(mp["branch"])
        daewoon = daewoon_pillars(dt, month_stem_idx, month_branch_idx, gender)

    pillars = {key: _enrich(p) for key, p in pillars.items()}

    # 음력 표기용
    cal = KoreanLunarCalendar()
    cal.setSolarDate(solar_dt.year, solar_dt.month, solar_dt.day)

    return {
        "solar": {"year": solar_dt.year, "month": solar_dt.month, "day": solar_dt.day},
        "lunar": cal.LunarIsoFormat(),
        "pillars": pillars,
        "elements": elements,
        "daewoon": daewoon,
        "seun": seun_pillars(),
    }
