"""합충형파해(合沖刑破害) 판정. plan/active/05-saju-analysis-engine.md §6.6.

`branch_relation`/`is_stem_hap`은 saju/compat.py(궁합 점수 로직)가 그대로 가져다 쓰는
기존 API라 시그니처·동작을 바꾸지 않는다 (tests/test_compat.py로 고정됨).
`stem_relations`/`branch_relations`는 4주 전체 조합을 다루는 신규 API (05 계획용).

⚠️ stem_relations/branch_relations의 개별 관계 판정 표(STEM_HAP 등)는 위키백과 등
표준 자료로 검증했지만, "4주 전체에서 어떤 조합을 묶어 보여줄지"의 집계 방식 자체는
참조 앱의 해당 화면(사주관계 > 천간과 지지) 스크린샷으로 대조하지 못했다
(plan 05 §9 — 사용자 제공 대기 항목). 개별 표는 신뢰도가 높으나 출력 형식은
검수 대상으로 남겨둔다.
"""

from __future__ import annotations

import itertools

from .gapja import EARTHLY_BRANCHES, HEAVENLY_STEMS
from .tables_analysis import (
    BANGHAP,
    BRANCH_CHUNG,
    BRANCH_HAE,
    BRANCH_HYEONG,
    BRANCH_PA,
    SAMHAP,
    STEM_CHUNG,
    STEM_HAP,
    WONJIN,
    YUKHAP,
)

PILLAR_LABEL = {"year": "년", "month": "월", "day": "일", "hour": "시"}
SELF_PUNISH_BRANCHES = {4, 6, 9, 11}  # 진 오 유 해 (자형)


# ── 기존 compat.py API (동작 불변, 궁합 점수 로직 전용) ────────────
def branch_relation(idx1: int, idx2: int) -> str | None:
    """두 지지의 관계: 'yukhap' | 'samhap' | 'chung' | 'wonjin' | None."""
    pair = frozenset((idx1 % 12, idx2 % 12))
    if len(pair) == 1:
        return None  # 같은 지지는 별도 가감 없음
    if pair in YUKHAP:
        return "yukhap"
    if pair in BRANCH_CHUNG:
        return "chung"
    if pair in WONJIN:
        return "wonjin"
    if any(pair <= group for group in SAMHAP):
        return "samhap"
    return None


def is_stem_hap(idx1: int, idx2: int) -> bool:
    """두 천간이 천간합인지."""
    return frozenset((idx1 % 10, idx2 % 10)) in STEM_HAP


# ── 신규 API: 4주 전체 합충형파해 목록 (05 계획용) ─────────────────
def stem_relations(pillars: dict) -> list[dict]:
    """4주 천간 조합의 천간합·천간충 목록.

    pillars: {'year': stem_char, 'month': ..., 'day': ..., 'hour': stem_char|None}
    """
    present = [(k, v) for k, v in pillars.items() if v]
    results: list[dict] = []
    for (k1, s1), (k2, s2) in itertools.combinations(present, 2):
        pair = frozenset((HEAVENLY_STEMS.index(s1), HEAVENLY_STEMS.index(s2)))
        if pair in STEM_HAP:
            results.append({
                "kind": "천간합", "pillars": [PILLAR_LABEL[k1], PILLAR_LABEL[k2]],
                "chars": [s1, s2], "note": f"{s1}{s2}합 ({STEM_HAP[pair]})",
            })
        elif pair in STEM_CHUNG:
            results.append({
                "kind": "천간충", "pillars": [PILLAR_LABEL[k1], PILLAR_LABEL[k2]],
                "chars": [s1, s2], "note": f"{s1}{s2}충",
            })
    return results


def branch_relations(pillars: dict) -> list[dict]:
    """4주 지지 조합의 육합·삼합·방합·충·형·파·해·원진 목록.

    pillars: {'year': branch_char, 'month': ..., 'day': ..., 'hour': branch_char|None}
    """
    present = [(k, v) for k, v in pillars.items() if v]

    def idx_of(br: str) -> int:
        return EARTHLY_BRANCHES.index(br)

    results: list[dict] = []
    covered_pairs: set[frozenset] = set()

    # 1) 삼합/방합 (3글자 모두 있으면 '삼합'|'방합', 2글자만 있으면 '반합').
    #    완전한 3글자 조합(full)일 때만 그 쌍들을 2) 단계에서 건너뛴다 — 반합(2글자)은
    #    별개의 명명된 관계(예: 육합)일 수도 있으므로 억제하지 않는다.
    for table, base_kind in ((SAMHAP, "삼합"), (BANGHAP, "방합")):
        for group, element in table.items():
            hits = [(k, br) for k, br in present if idx_of(br) in group]
            distinct = {idx_of(br) for _, br in hits}
            if len(distinct) < 2:
                continue
            is_full = len(distinct) == 3
            kind = base_kind if is_full else f"반{base_kind}"
            results.append({
                "kind": kind,
                "pillars": [PILLAR_LABEL[k] for k, _ in hits],
                "chars": sorted({br for _, br in hits}, key=idx_of),
                "note": f"{element}국 {kind}",
            })
            if is_full:
                covered_pairs.update(
                    frozenset(pair) for pair in itertools.combinations(sorted(distinct), 2)
                )

    # 2) 나머지 2지지 관계 (육합/충/형/파/해/원진). 이미 삼합/방합으로 설명된 쌍은 건너뛴다.
    pair_tables = [
        (YUKHAP, "육합"), (BRANCH_CHUNG, "충"),
        (BRANCH_PA, "파"), (BRANCH_HAE, "해"), (WONJIN, "원진"),
    ]
    for (k1, b1), (k2, b2) in itertools.combinations(present, 2):
        i1, i2 = idx_of(b1), idx_of(b2)
        if i1 == i2:
            if i1 in SELF_PUNISH_BRANCHES:
                results.append({
                    "kind": "형", "pillars": [PILLAR_LABEL[k1], PILLAR_LABEL[k2]],
                    "chars": [b1, b2], "note": f"{b1}{b2} 자형(自刑)",
                })
            continue

        pair = frozenset((i1, i2))
        if pair in covered_pairs:
            continue

        matched = False
        for table, kind in pair_tables:
            if pair in table:
                results.append({
                    "kind": kind, "pillars": [PILLAR_LABEL[k1], PILLAR_LABEL[k2]],
                    "chars": [b1, b2], "note": f"{b1}{b2} {kind}",
                })
                matched = True
                break
        if matched:
            continue
        for group in BRANCH_HYEONG:
            if len(group) == 3 and pair <= group:
                results.append({
                    "kind": "형", "pillars": [PILLAR_LABEL[k1], PILLAR_LABEL[k2]],
                    "chars": [b1, b2], "note": f"{b1}{b2} 형(刑)",
                })
                break

    return results
