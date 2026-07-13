"""커플 궁합(합·충·오행 보완) 계산.

점수 규칙은 plan/done/DESIGN_GUNGHAP.md 참고. 기본 50점에서 요인별로 가감해 0~100으로 클램프한다.
"""

from __future__ import annotations

from .gapja import (
    BRANCH_ANIMALS,
    BRANCHES_HANJA,
    EARTHLY_BRANCHES,
    HEAVENLY_STEMS,
)
from itertools import combinations

from .relations import branch_relation, is_stem_hap
from .tables_analysis import GENERATES

# 궁합 점수 로직이 계속 saju.compat.branch_relation / is_stem_hap 로 임포트할 수 있도록
# 재노출한다 (구현은 saju/relations.py §6.6로 이동, 동작은 동일).
__all__ = [
    "branch_relation", "is_stem_hap", "couple_compat", "team_compat",
    "day_stem_relation", "zodiac_of",
]

ELEMENTS = ["목", "화", "토", "금", "수"]

GRADES = [
    (90, "천생연분"),
    (80, "환상의 짝꿍"),
    (70, "아주 좋은 궁합"),
    (60, "좋은 궁합"),
    (50, "무난한 궁합"),
    (40, "노력이 필요한 궁합"),
    (0, "서로 이해가 필요한 궁합"),
]


def _branch_pair_label(b1: str, b2: str) -> str:
    h1 = BRANCHES_HANJA[EARTHLY_BRANCHES.index(b1)]
    h2 = BRANCHES_HANJA[EARTHLY_BRANCHES.index(b2)]
    return f"{b1}({h1})·{b2}({h2})"


# (관계, 영역) → (점수, 설명)
_BRANCH_FACTOR_RULES = {
    ("yukhap", "day"): (12, "서로에게 자연스럽게 끌리는 찰떡 조합이에요."),
    ("samhap", "day"): (10, "함께 있을 때 시너지가 나는 조합이에요."),
    ("chung", "day"): (-12, "부딪히기 쉬운 조합이라 배려가 필요해요."),
    ("wonjin", "day"): (-8, "이유 없이 서운해지기 쉬운 조합이니 대화가 중요해요."),
    ("yukhap", "year"): (8, "띠끼리 합이 들어 잘 통하는 인연이에요."),
    ("samhap", "year"): (8, "띠 삼합! 주변에서도 잘 어울린다는 말을 들어요."),
    ("chung", "year"): (-8, "띠끼리 충이라 취향 차이가 클 수 있어요."),
    ("wonjin", "year"): (-5, "띠 원진이라 가끔 엇갈릴 수 있지만 노력으로 극복돼요."),
}

_RELATION_NAMES = {"yukhap": "육합", "samhap": "삼합", "chung": "충", "wonjin": "원진"}


def couple_compat(result1: dict, result2: dict) -> dict:
    """calculate_saju() 결과 두 개로 궁합을 계산.

    반환: {'score', 'grade', 'factors': [{'area','label','delta','desc'}],
           'complement_elements': [보완이 필요한 오행 최대 2개]}
    """
    p1, p2 = result1["pillars"], result2["pillars"]
    factors = []
    score = 50

    # ── 일간 천간합 ──
    s1 = HEAVENLY_STEMS.index(p1["day"]["stem"])
    s2 = HEAVENLY_STEMS.index(p2["day"]["stem"])
    if is_stem_hap(s1, s2):
        score += 15
        factors.append({
            "area": "일간",
            "label": f"일간 천간합 ({p1['day']['stem']}·{p2['day']['stem']})",
            "delta": 15,
            "desc": "타고난 성향이 서로를 완성해 주는 최고의 인연이에요.",
        })

    # ── 일지 · 띠(연지) 관계 ──
    for area_key, area_name, pkey in (("day", "일지", "day"), ("year", "띠", "year")):
        b1_str, b2_str = p1[pkey]["branch"], p2[pkey]["branch"]
        rel = branch_relation(
            EARTHLY_BRANCHES.index(b1_str), EARTHLY_BRANCHES.index(b2_str)
        )
        if rel is None:
            continue
        delta, desc = _BRANCH_FACTOR_RULES[(rel, area_key)]
        score += delta
        factors.append({
            "area": area_name,
            "label": f"{area_name} {_RELATION_NAMES[rel]} ({_branch_pair_label(b1_str, b2_str)})",
            "delta": delta,
            "desc": desc,
        })

    # ── 오행 상호보완 ──
    c1, c2 = result1["elements"], result2["elements"]
    filled = [el for el in ELEMENTS if (c1[el] == 0) != (c2[el] == 0)]
    both_missing = [el for el in ELEMENTS if c1[el] == 0 and c2[el] == 0]

    if filled:
        delta = min(len(filled) * 3, 12)
        score += delta
        factors.append({
            "area": "오행",
            "label": f"오행 보완 ({'·'.join(filled)})",
            "delta": delta,
            "desc": "한 사람에게 부족한 기운을 상대가 채워 주는 관계예요.",
        })
    if both_missing:
        delta = max(len(both_missing) * -2, -6)
        score += delta
        factors.append({
            "area": "오행",
            "label": f"둘 다 부족한 오행 ({'·'.join(both_missing)})",
            "delta": delta,
            "desc": "함께 이 기운을 채우는 활동(데이트 지역 추천 참고)이 도움이 돼요.",
        })

    score = max(0, min(100, score))
    grade = next(g for threshold, g in GRADES if score >= threshold)

    # ── 보완 오행: 합산 개수가 가장 부족한 오행 (추천 지역 근거) ──
    combined = {el: c1[el] + c2[el] for el in ELEMENTS}
    weak = sorted((el for el in ELEMENTS if combined[el] <= 1), key=lambda e: combined[e])
    if not weak:
        weak = [min(ELEMENTS, key=lambda e: combined[e])]
    complement = weak[:2]

    return {
        "score": score,
        "grade": grade,
        "factors": factors,
        "complement_elements": complement,
    }


def day_stem_pair_relation(element_a: str, element_b: str) -> str:
    """두 일간 오행의 관계: 'same'(비화) | 'gen'(상생) | 'ctrl'(상극).

    커플 궁합 데이트 화면의 일간 관계 뱃지(生/比/剋)에 쓰인다. couple_compat()의
    점수(천간합·육합·오행보완 종합)와는 별개로, "두 사람 일간의 오행이 어떤
    관계인가"라는 하나의 사실만 알려주는 지표다.
    """
    if element_a == element_b:
        return "same"
    if GENERATES[element_a] == element_b or GENERATES[element_b] == element_a:
        return "gen"
    return "ctrl"


def team_compat(results: list[dict]) -> dict:
    """calculate_saju() 결과 N개(3~4인)의 팀 궁합.

    기존 couple_compat()을 모든 쌍(i<j)에 적용해 평균낸 점수를 쓴다 — 검증된
    2인 궁합 엔진을 그대로 재사용해 새 점수 체계를 만들지 않는다.
    반환: {'score', 'grade', 'pairwise': [{'a','b','score','grade'}, ...]}
    """
    if len(results) < 2:
        raise ValueError("team_compat에는 최소 2명이 필요합니다.")
    pairwise = []
    for i, j in combinations(range(len(results)), 2):
        c = couple_compat(results[i], results[j])
        pairwise.append({"a": i, "b": j, "score": c["score"], "grade": c["grade"]})
    score = round(sum(p["score"] for p in pairwise) / len(pairwise))
    grade = next(g for threshold, g in GRADES if score >= threshold)
    return {"score": score, "grade": grade, "pairwise": pairwise}


def zodiac_of(result: dict) -> dict:
    """calculate_saju() 결과에서 띠 정보를 추출."""
    branch = result["pillars"]["year"]["branch"]
    idx = EARTHLY_BRANCHES.index(branch)
    return {
        "branch": branch,
        "hanja": BRANCHES_HANJA[idx],
        "animal": BRANCH_ANIMALS[idx],
    }
