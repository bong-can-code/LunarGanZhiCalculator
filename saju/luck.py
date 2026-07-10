"""대운(大運)·세운(歲運) 계산.

- 대운 순행/역행: 연간(年干)의 음양과 성별로 정한다.
  양간(갑병무경임) + 남자, 또는 음간(을정기신계) + 여자 → 순행.
  그 반대 조합은 역행.
- 대운수(대운이 바뀌는 나이 기준): 태어난 시각으로부터 다음 절(순행) 또는
  직전 절(역행)까지의 일수를 3으로 나눠 근사한다("3일=1년" 통상 규칙).
- 대운 간지: 월주를 기준으로 순행이면 다음 갑자, 역행이면 이전 갑자로 10년마다 진행한다.
- 세운: 특정 연도의 연주. 절기와 무관하게 "그 해"를 가리키도록 6월 1일 기준으로 계산한다.
"""

from __future__ import annotations

from datetime import datetime

from .gapja import HEAVENLY_STEMS, gapja_index, pillar
from .pillars import year_pillar
from .solar_terms import MONTH_TERMS, solar_term_datetime


def is_forward(year_stem_idx: int, gender: str) -> bool:
    """연간 음양과 성별로 대운 순행 여부를 판정. gender는 'male' 또는 'female'."""
    is_yang_year = year_stem_idx % 2 == 0
    is_male = gender == "male"
    return is_yang_year == is_male


def _term_boundaries(dt: datetime) -> list[datetime]:
    boundaries = []
    for yr in (dt.year - 1, dt.year, dt.year + 1):
        for _, lon in MONTH_TERMS:
            boundaries.append(solar_term_datetime(yr, lon))
    boundaries.sort()
    return boundaries


def daewoon_start_age(dt: datetime, forward: bool) -> int:
    """대운수(순행: 다음 절까지, 역행: 직전 절부터 경과한 일수 / 3, 최소 1)."""
    boundaries = _term_boundaries(dt)
    if forward:
        boundary = next(b for b in boundaries if b > dt)
    else:
        boundary = next(b for b in reversed(boundaries) if b <= dt)
    days = abs((boundary - dt).total_seconds()) / 86400
    return max(round(days / 3), 1)


def daewoon_pillars(
    dt: datetime,
    month_stem_idx: int,
    month_branch_idx: int,
    gender: str,
    count: int = 9,
) -> dict:
    """대운 리스트. {'direction', 'start_age', 'pillars': [{'age', ...간지}, ...]}."""
    year_stem_idx = HEAVENLY_STEMS.index(year_pillar(dt)["stem"])
    forward = is_forward(year_stem_idx, gender)
    start_age = daewoon_start_age(dt, forward)

    base_index = gapja_index(month_stem_idx, month_branch_idx)
    step = 1 if forward else -1
    pillars = []
    for k in range(1, count + 1):
        idx = (base_index + step * k) % 60
        pillars.append({"age": start_age + (k - 1) * 10, **pillar(idx % 10, idx % 12)})

    return {
        "direction": "순행" if forward else "역행",
        "start_age": start_age,
        "pillars": pillars,
    }


def seun_pillars(center_year: int | None = None, span: int = 4) -> list[dict]:
    """세운(연도별 연주) 리스트. center_year 생략 시 현재 연도를 기준으로 한다."""
    if center_year is None:
        center_year = datetime.now().year
    result = []
    for y in range(center_year - span, center_year + span + 1):
        # 절기 무관하게 "그 해"를 가리키도록 입춘 이후 시점(6월 1일)으로 계산한다.
        result.append({"year": y, **year_pillar(datetime(y, 6, 1))})
    return result
