"""사주 계산 엔진 검증 테스트.

일주 앵커는 외부 권위 출처로 교차검증했다:
- 1949-10-01 = 갑자일 (Wikipedia, Sexagenary cycle)
- 2024-01-01 = 갑자일 (KASI 표준 korean-lunar-calendar)
연/월/시주는 오호둔(五虎遁)·오서둔(五鼠遁) 규칙과 절기 경계로 검증한다.
"""

import datetime

import pytest

from saju import calculate_saju
from saju.pillars import (
    EARTHLY_BRANCHES,
    HEAVENLY_STEMS,
    _day_gapja_index,
    hour_pillar,
)
from saju.solar_terms import solar_term_datetime


def _hanja(r, key):
    return r["pillars"][key]["hanja"]


# ── 일주 외부 앵커 ────────────────────────────────────────────
@pytest.mark.parametrize("y,m,d,expected", [
    (1949, 10, 1, "갑자"),   # Wikipedia Sexagenary cycle 예시
    (2024, 1, 1, "갑자"),    # KASI 표준
])
def test_day_pillar_external_anchor(y, m, d, expected):
    idx = _day_gapja_index(datetime.date(y, m, d))
    got = HEAVENLY_STEMS[idx % 10] + EARTHLY_BRANCHES[idx % 12]
    assert got == expected


def test_day_cycle_continuity():
    a = _day_gapja_index(datetime.date(1949, 10, 1))
    b = _day_gapja_index(datetime.date(1949, 10, 2))
    assert (b - a) % 60 == 1


# ── 4주 종합 검증 (오호둔·오서둔·절기 규칙) ───────────────────
@pytest.mark.parametrize("y,m,d,h,year,month,day,hour", [
    (1990, 5, 15, 14, "庚午", "辛巳", "庚辰", "癸未"),
    (2024, 1, 1, 0, "癸卯", "甲子", "甲子", "甲子"),   # 입춘 전 → 계묘년(전년)
    (1985, 2, 4, 10, "乙丑", "戊寅", "甲戌", "己巳"),  # 입춘 당일 오전 → 을축년
    (2000, 1, 1, 12, "己卯", "丙子", "戊午", "戊午"),
])
def test_full_saju(y, m, d, h, year, month, day, hour):
    r = calculate_saju(y, m, d, h)
    assert _hanja(r, "year") == year
    assert _hanja(r, "month") == month
    assert _hanja(r, "day") == day
    assert _hanja(r, "hour") == hour


# ── 연주 입춘 경계 ────────────────────────────────────────────
def test_year_boundary_before_ipchun():
    """입춘 직전은 전년 간지여야 한다."""
    ipchun = solar_term_datetime(1985, 315)  # 1985-02-04 경
    before = calculate_saju(1985, 2, 3, 0)   # 입춘 전날
    assert _hanja(before, "year") == "甲子"    # 1984년 = 갑자년
    after = calculate_saju(1985, 2, 5, 0)    # 입춘 다음날
    assert _hanja(after, "year") == "乙丑"     # 1985년 = 을축년


# ── 정자시(23시) 날짜 전환 ────────────────────────────────────
def test_jeongjasi_day_shift():
    """23시 출생은 다음날 일주를 쓴다(정자시)."""
    at_22 = calculate_saju(2024, 1, 1, 22)  # 당일 일주
    at_23 = calculate_saju(2024, 1, 1, 23)  # 다음날(2024-01-02) 일주
    assert _hanja(at_22, "day") == "甲子"
    assert _hanja(at_23, "day") == "乙丑"    # 갑자 다음 = 을축


# ── 음력 입력 ────────────────────────────────────────────────
def test_lunar_input_matches_solar():
    """음력 입력을 양력으로 변환한 결과가 동일 양력 계산과 일치."""
    # 1990-05-15(양) = 음력 1990-04-21
    solar = calculate_saju(1990, 5, 15, 14)
    lunar = calculate_saju(1990, 4, 21, 14, is_lunar=True)
    assert lunar["solar"] == {"year": 1990, "month": 5, "day": 15}
    assert _hanja(lunar, "day") == _hanja(solar, "day")


# ── 시간 모름 → 시주 생략 ─────────────────────────────────────
def test_no_hour():
    r = calculate_saju(1990, 5, 15, None)
    assert r["pillars"]["hour"] is None
    assert _hanja(r, "day") == "庚辰"


# ── 잘못된 입력 ──────────────────────────────────────────────
def test_invalid_date():
    with pytest.raises(ValueError):
        calculate_saju(2024, 2, 30, 0)  # 존재하지 않는 날짜


# ── 시주 오서둔 규칙 스팟 체크 ────────────────────────────────
@pytest.mark.parametrize("day_stem,hour,expected", [
    ("갑", 0, "甲子"),   # 갑일 자시 → 갑자
    ("무", 12, "戊午"),  # 무일 오시 → 무오
    ("경", 14, "癸未"),  # 경일 미시 → 계미
])
def test_hour_rule(day_stem, hour, expected):
    idx = HEAVENLY_STEMS.index(day_stem)
    assert hour_pillar(idx, hour)["hanja"] == expected
