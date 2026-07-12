"""12신살·공망·신살/길성. plan/active/05-saju-analysis-engine.md §6.3~§6.5."""

from __future__ import annotations

from .gapja import EARTHLY_BRANCHES, gapja_index
from .tables_analysis import (
    AMROK,
    BAEKHO_DAESAL,
    CHEONDEOK_GWIIN,
    CHEONEUL_GWIIN,
    GEONROK,  # noqa: F401 — 건록 자체는 미사용, 자산 완결성을 위해 함께 노출
    GEUPGAK_SAL,
    HYEONCHIM_SAL_BRANCHES,
    HYEONCHIM_SAL_STEMS,
    MUNCHANG_GWIIN,
    SAMHAP_GEOPSAL_START,
    SAMHAP_GROUP_OF_BRANCH,
    SEASON_OF_BRANCH,
    SINSAL12_ORDER,
    UNSEONG12_ANCHOR,
    WOLDEOK_GWIIN,
)


def sinsal12_of(base_branch: str, target_branch: str) -> str:
    """기준 지지(삼합국)로부터 대상 지지의 12신살."""
    group = SAMHAP_GROUP_OF_BRANCH[base_branch]
    start_idx = EARTHLY_BRANCHES.index(SAMHAP_GEOPSAL_START[group])
    target_idx = EARTHLY_BRANCHES.index(target_branch)
    offset = (target_idx - start_idx) % 12
    return SINSAL12_ORDER[offset]


def gongmang_of(day_stem_idx: int, day_branch_idx: int) -> list[str]:
    """일주의 순중공망(旬中空亡) 지지 2개."""
    i = gapja_index(day_stem_idx, day_branch_idx)
    xun_start_branch_idx = (i - (i % 10)) % 12
    return [
        EARTHLY_BRANCHES[(xun_start_branch_idx + 10) % 12],
        EARTHLY_BRANCHES[(xun_start_branch_idx + 11) % 12],
    ]


def gilseong_of(pillars: dict) -> dict:
    """4주(년/월/일/시)의 신살·길성 태그.

    pillars: {'year': {'stem','branch'}, 'month': {...}, 'day': {...}, 'hour': {...}|None}
    반환: {'stems': {pillar_key: [tags]}, 'branches': {pillar_key: [tags]}}
    """
    day_stem = pillars["day"]["stem"]
    day_branch = pillars["day"]["branch"]
    year_branch = pillars["year"]["branch"]
    month_branch = pillars["month"]["branch"]

    samhap_group = SAMHAP_GROUP_OF_BRANCH[month_branch]
    season = SEASON_OF_BRANCH[month_branch]
    geupgak_branches = GEUPGAK_SAL[season]
    cheondeok_kind, cheondeok_char = CHEONDEOK_GWIIN[month_branch]
    woldeok_stem = WOLDEOK_GWIIN[samhap_group]

    munchang_branch = MUNCHANG_GWIIN[day_stem]
    mungok_branch = EARTHLY_BRANCHES[(EARTHLY_BRANCHES.index(munchang_branch) + 6) % 12]
    hakdang_branch = UNSEONG12_ANCHOR[day_stem][0]

    tags_stem: dict[str, list[str]] = {}
    tags_branch: dict[str, list[str]] = {}

    for key in ("year", "month", "day", "hour"):
        p = pillars.get(key)
        if p is None:
            tags_stem[key] = []
            tags_branch[key] = []
            continue

        stem, branch = p["stem"], p["branch"]
        s_tags: list[str] = []
        b_tags: list[str] = []

        if stem in HYEONCHIM_SAL_STEMS:
            s_tags.append("현침살")
        if branch in HYEONCHIM_SAL_BRANCHES:
            b_tags.append("현침살")

        if branch in CHEONEUL_GWIIN[day_stem]:
            b_tags.append("천을귀인")

        if cheondeok_kind == "stem" and stem == cheondeok_char:
            s_tags.append("천덕귀인")
        elif cheondeok_kind == "branch" and branch == cheondeok_char:
            b_tags.append("천덕귀인")

        if stem == woldeok_stem:
            s_tags.append("월덕귀인")

        if (stem, branch) in BAEKHO_DAESAL:
            s_tags.append("백호대살")
            b_tags.append("백호대살")

        if key != "month" and branch in geupgak_branches:
            b_tags.append("급각살")

        if (
            sinsal12_of(year_branch, branch) == "화개살"
            or sinsal12_of(day_branch, branch) == "화개살"
        ):
            b_tags.append("화개살")

        if branch == mungok_branch:
            b_tags.append("문곡귀인")
        if branch == hakdang_branch:
            b_tags.append("학당귀인")
        if branch == AMROK[day_stem]:
            b_tags.append("암록")

        tags_stem[key] = s_tags
        tags_branch[key] = b_tags

    return {"stems": tags_stem, "branches": tags_branch}
