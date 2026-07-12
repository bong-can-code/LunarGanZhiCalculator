"""사주 계산 오케스트레이션 + 음/양력 입력 처리 + 명리 분석 레이어.

명리 분석(십성·12운성·12신살·공망·신살길성·합충형파해·오행%·신강신약)의
규칙 표·검증 근거는 plan/active/05-saju-analysis-engine.md와
docs/expert-review/saju-analysis-rules.md(전문가 검수용)를 참고.
"""

from __future__ import annotations

from datetime import datetime

from korean_lunar_calendar import KoreanLunarCalendar

from .gapja import EARTHLY_BRANCHES, HEAVENLY_STEMS, STEM_ELEMENT, STEMS_HANJA
from .luck import daewoon_pillars, seun_pillars
from .pillars import (
    day_pillar,
    hour_pillar,
    month_pillar,
    year_pillar,
)
from .relations import branch_relations, stem_relations
from .sinsal import gilseong_of, gongmang_of, sinsal12_of
from .sipseong import sipseong_of, sipseong_of_branch
from .strength import (
    day_master_strength,
    element_percentages,
    element_status_all,
    sipseong_breakdown,
)
from .tables import count_elements, hidden_stems, nayin_of
from .unseong import unseong12_of


def _yin_yang(index: int) -> str:
    return "양" if index % 2 == 0 else "음"


def _enrich(p: dict | None) -> dict | None:
    """4주 간지에 지장간·납음오행·음양을 덧붙인다."""
    if p is None:
        return None
    stem_idx = HEAVENLY_STEMS.index(p["stem"])
    branch_idx = EARTHLY_BRANCHES.index(p["branch"])
    return {
        **p,
        "hidden_stems": hidden_stems(p["branch"]),
        "nayin": nayin_of(stem_idx, branch_idx),
        "yin_yang_stem": _yin_yang(stem_idx),
        "yin_yang_branch": _yin_yang(branch_idx),
    }


def _add_pillar_analysis(
    p: dict | None, *, day_stem: str, year_branch: str, gongmang_branches: list[str], is_day: bool
) -> dict | None:
    """지장간·납음이 붙은 기둥 dict에 십성·12운성·12신살·공망 여부를 덧붙인다."""
    if p is None:
        return None
    return {
        **p,
        "sipseong_stem": "일원" if is_day else sipseong_of(day_stem, p["stem"]),
        "sipseong_branch": sipseong_of_branch(day_stem, p["branch"]),
        "unseong12": unseong12_of(day_stem, p["branch"]),
        "sinsal12": sinsal12_of(year_branch, p["branch"]),
        "is_gongmang": p["branch"] in gongmang_branches,
    }


def _add_luck_analysis(items: list[dict], day_stem: str) -> list[dict]:
    """대운/세운 리스트 각 항목에 십성·12운성 라벨을 덧붙인다."""
    return [
        {
            **item,
            "sipseong_stem": sipseong_of(day_stem, item["stem"]),
            "sipseong_branch": sipseong_of_branch(day_stem, item["branch"]),
            "unseong12": unseong12_of(day_stem, item["branch"]),
        }
        for item in items
    ]


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
    반환: {'solar', 'lunar', 'pillars', 'elements', 'daewoon', 'seun',
           'day_master', 'gongmang', 'gilseong', 'relations', 'analysis'}
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

    day_stem = dp["stem"]
    day_branch_idx = EARTHLY_BRANCHES.index(dp["branch"])
    gongmang_branches = gongmang_of(day_stem_idx, day_branch_idx)

    daewoon = None
    if gender is not None:
        month_stem_idx = HEAVENLY_STEMS.index(mp["stem"])
        month_branch_idx = EARTHLY_BRANCHES.index(mp["branch"])
        daewoon = daewoon_pillars(dt, month_stem_idx, month_branch_idx, gender)
        daewoon = {**daewoon, "pillars": _add_luck_analysis(daewoon["pillars"], day_stem)}

    seun = _add_luck_analysis(seun_pillars(), day_stem)

    # 지장간·납음·음양 → 십성·12운성·12신살·공망 순서로 2단계 enrich.
    enriched = {key: _enrich(p) for key, p in pillars.items()}
    analysed_pillars = {
        key: _add_pillar_analysis(
            p, day_stem=day_stem, year_branch=yp["branch"],
            gongmang_branches=gongmang_branches, is_day=(key == "day"),
        )
        for key, p in enriched.items()
    }

    gilseong_input = {
        key: ({"stem": p["stem"], "branch": p["branch"]} if p else None)
        for key, p in pillars.items()
    }
    gilseong = gilseong_of(gilseong_input)
    relations = {
        "stems": stem_relations({k: (p["stem"] if p else None) for k, p in pillars.items()}),
        "branches": branch_relations({k: (p["branch"] if p else None) for k, p in pillars.items()}),
    }

    analysis = {
        "elements_pct": element_percentages(pillars),
        "element_status": element_status_all(pillars),
        **sipseong_breakdown(pillars),
        "strength": day_master_strength(pillars),
    }

    # 음력 표기용
    cal = KoreanLunarCalendar()
    cal.setSolarDate(solar_dt.year, solar_dt.month, solar_dt.day)

    return {
        "solar": {"year": solar_dt.year, "month": solar_dt.month, "day": solar_dt.day},
        "lunar": cal.LunarIsoFormat(),
        "pillars": analysed_pillars,
        "elements": elements,
        "daewoon": daewoon,
        "seun": seun,
        "day_master": {
            "stem": day_stem,
            "hanja": STEMS_HANJA[day_stem_idx],
            "element": STEM_ELEMENT[day_stem],
            "yin_yang": _yin_yang(day_stem_idx),
        },
        "gongmang": gongmang_branches,
        "gilseong": gilseong,
        "relations": relations,
        "analysis": analysis,
    }
