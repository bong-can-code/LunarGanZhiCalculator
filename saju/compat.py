"""커플 궁합(합·충·오행 보완) 계산.

점수 규칙은 plan/done/DESIGN_GUNGHAP.md 4장 참고. 기본 50점에서 요인별로 가감해 0~100으로 클램프한다.
"""

from __future__ import annotations

from .gapja import (
    BRANCH_ANIMALS,
    BRANCHES_HANJA,
    EARTHLY_BRANCHES,
    HEAVENLY_STEMS,
)

# ── 지지 관계 (EARTHLY_BRANCHES 인덱스 기준) ─────────────────────
# 육합: 자축, 인해, 묘술, 진유, 사신, 오미
YUKHAP_PAIRS = {frozenset(p) for p in [(0, 1), (2, 11), (3, 10), (4, 9), (5, 8), (6, 7)]}
# 충: 마주보는 지지 (자오, 축미, 인신, 묘유, 진술, 사해)
CHUNG_PAIRS = {frozenset((i, i + 6)) for i in range(6)}
# 삼합: 신자진(수), 해묘미(목), 인오술(화), 사유축(금)
SAMHAP_GROUPS = [
    frozenset({8, 0, 4}), frozenset({11, 3, 7}),
    frozenset({2, 6, 10}), frozenset({5, 9, 1}),
]
# 원진: 자미, 축오, 인유, 묘신, 진해, 사술
WONJIN_PAIRS = {frozenset(p) for p in [(0, 7), (1, 6), (2, 9), (3, 8), (4, 11), (5, 10)]}

# 천간합: 갑기, 을경, 병신, 정임, 무계 (인덱스 i와 i+5)
STEM_HAP_PAIRS = {frozenset((i, i + 5)) for i in range(5)}

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


def branch_relation(idx1: int, idx2: int) -> str | None:
    """두 지지의 관계: 'yukhap' | 'samhap' | 'chung' | 'wonjin' | None."""
    pair = frozenset((idx1 % 12, idx2 % 12))
    if len(pair) == 1:
        return None  # 같은 지지는 별도 가감 없음
    if pair in YUKHAP_PAIRS:
        return "yukhap"
    if pair in CHUNG_PAIRS:
        return "chung"
    if pair in WONJIN_PAIRS:
        return "wonjin"
    if any(pair <= group for group in SAMHAP_GROUPS):
        return "samhap"
    return None


def is_stem_hap(idx1: int, idx2: int) -> bool:
    """두 천간이 천간합인지."""
    return frozenset((idx1 % 10, idx2 % 10)) in STEM_HAP_PAIRS


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


def zodiac_of(result: dict) -> dict:
    """calculate_saju() 결과에서 띠 정보를 추출."""
    branch = result["pillars"]["year"]["branch"]
    idx = EARTHLY_BRANCHES.index(branch)
    return {
        "branch": branch,
        "hanja": BRANCHES_HANJA[idx],
        "animal": BRANCH_ANIMALS[idx],
    }
