"""사주 사주(四柱, 네 기둥) 간지 계산.

정통 명리 기준:
- 연주(年柱): 입춘(立春)을 연 경계로 삼는다. 입춘 전이면 전년 간지.
- 월주(月柱): 12절(節)로 월 경계를 잡고, 연간(年干)에 오호둔(五虎遁)을 적용해 월간 결정.
- 일주(日柱): 60갑자 일 순환. KASI 표준(korean-lunar-calendar)의 일간지를 사용.
- 시주(時柱): 정자시(23:00 날짜 전환) 기준. 일간(日干)에 오서둔(五鼠遁) 적용.

일/시 경계는 정자시(正子時)를 채택한다: 23:00를 하루의 시작으로 보아 23:00~23:59 출생은
다음날 일주를 쓴다. (야자시/조자시 학설은 소수설이라 채택하지 않음.)
"""

from __future__ import annotations

from datetime import datetime, timedelta

from korean_lunar_calendar import KoreanLunarCalendar

from .solar_terms import MONTH_TERMS, solar_term_datetime

HEAVENLY_STEMS = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
EARTHLY_BRANCHES = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]

STEMS_HANJA = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES_HANJA = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


def _pillar(stem_idx: int, branch_idx: int) -> dict:
    return {
        "stem": HEAVENLY_STEMS[stem_idx % 10],
        "branch": EARTHLY_BRANCHES[branch_idx % 12],
        "hanja": STEMS_HANJA[stem_idx % 10] + BRANCHES_HANJA[branch_idx % 12],
        "korean": HEAVENLY_STEMS[stem_idx % 10] + EARTHLY_BRANCHES[branch_idx % 12],
    }


def _saju_year(dt: datetime) -> int:
    """입춘 기준 사주 연도. 입춘 절입시각 이전이면 전년으로 본다."""
    ipchun = solar_term_datetime(dt.year, 315)
    return dt.year if dt >= ipchun else dt.year - 1


def year_pillar(dt: datetime) -> dict:
    """연주: 입춘 기준. (기원후 4년 = 갑자년)"""
    sy = _saju_year(dt)
    stem_idx = (sy - 4) % 10
    branch_idx = (sy - 4) % 12
    return _pillar(stem_idx, branch_idx)


def _month_ordinal(dt: datetime) -> int:
    """12절 기준으로 인월(寅月)=0 부터의 월 순번(0~11)을 반환.

    입춘~경칩=인월(0), 경칩~청명=묘월(1), ... 소한~입춘=축월(11).
    """
    # 인접 연도의 12절 절입시각을 모아 birth 시각이 어느 절 구간인지 찾는다.
    boundaries = []  # (절입시각, 인월기준 순번)
    for yr in (dt.year - 1, dt.year, dt.year + 1):
        for ordinal, (_, lon) in enumerate(MONTH_TERMS):
            boundaries.append((solar_term_datetime(yr, lon), ordinal))
    boundaries.sort(key=lambda x: x[0])
    ordinal = None
    for term_dt, term_ord in boundaries:
        if term_dt <= dt:
            ordinal = term_ord
        else:
            break
    if ordinal is None:
        raise ValueError("월주 절기 구간을 찾지 못함")
    return ordinal


def month_pillar(dt: datetime, year_stem_idx: int) -> dict:
    """월주: 12절 기준 월 + 오호둔(五虎遁) 월간.

    오호둔: 인월(寅月)의 천간 = (연간 % 5) * 2 + 2 (mod 10).
    갑기년→병인월, 을경년→무인월, 병신년→경인월, 정임년→임인월, 무계년→갑인월.
    """
    ordinal = _month_ordinal(dt)  # 인월=0 기준
    yin_month_stem = ((year_stem_idx % 5) * 2 + 2) % 10
    stem_idx = (yin_month_stem + ordinal) % 10
    branch_idx = (2 + ordinal) % 12  # 인(寅)=2 부터 시작
    return _pillar(stem_idx, branch_idx)


def _day_gapja_index(date_ymd) -> int:
    """해당 양력 날짜의 일간지 인덱스(0~59, 0=갑자). KASI 표준 사용."""
    cal = KoreanLunarCalendar()
    cal.setSolarDate(date_ymd.year, date_ymd.month, date_ymd.day)
    # korean-lunar-calendar 내부 일간지 인덱스를 문자열로 역산
    gapja = cal.getGapJaString().split()  # ['계묘년','갑자월','갑자일']
    day = gapja[2]  # '갑자일'
    stem = HEAVENLY_STEMS.index(day[0])
    branch = EARTHLY_BRANCHES.index(day[1])
    # (stem, branch) → 60갑자 인덱스
    for i in range(60):
        if i % 10 == stem and i % 12 == branch:
            return i
    raise ValueError("일간지 인덱스 산출 실패")


def day_pillar(dt: datetime, use_jeongjasi: bool = True) -> tuple[dict, int]:
    """일주. 정자시면 23시 이후 출생은 다음날 일주. (일간 인덱스도 함께 반환)"""
    day_date = dt.date()
    if use_jeongjasi and dt.hour == 23:
        day_date = (dt + timedelta(days=1)).date()
    idx = _day_gapja_index(day_date)
    return _pillar(idx % 10, idx % 12), idx % 10


def hour_pillar(day_stem_idx: int, hour: int) -> dict:
    """시주: 오서둔(五鼠遁) 기준.

    자시(子時) 천간 = (일간 % 5) * 2 (mod 10).
    갑기일→갑자시, 을경일→병자시, 병신일→무자시, 정임일→경자시, 무계일→임자시.
    시지: 23~1시=자, 1~3시=축 ... ((hour+1)//2) % 12.
    """
    branch_idx = ((hour + 1) // 2) % 12
    zi_stem = ((day_stem_idx % 5) * 2) % 10
    stem_idx = (zi_stem + branch_idx) % 10
    return _pillar(stem_idx, branch_idx)
