"""오행%·십성그룹·상태배지·신강신약. plan/active/05-saju-analysis-engine.md §6.7~§6.8.

⚠️ day_master_strength()는 §6.8에 명시된 대로 "참조용 간이 판정"이다. 신강신약은
유파별 편차가 가장 큰 항목이라 골든 스크린샷 대조 없이 설계했다 (plan §9 — 사용자가
신강신약 탭 스크린샷을 제공하면 등급 경계·가중치를 튜닝한다). 반드시 명리학
전문가 검수를 거치기 전에는 "참고용" 표기를 달아 노출할 것.
"""

from __future__ import annotations

from .gapja import STEM_ELEMENT
from .sipseong import sipseong_group, sipseong_of, sipseong_of_branch
from .tables import count_elements
from .tables_analysis import CONTROLS, GENERATES

ELEMENTS = ["목", "화", "토", "금", "수"]
ALL_SIPSEONG = [
    "비견", "겁재", "식신", "상관", "편재", "정재", "편관", "정관", "편인", "정인",
]

# 오행 X → (X를 극하는 오행, X를 생하는 오행). GROUP_ELEMENT_MAP에서 역참조로 사용.
_CONTROLS_INV = {v: k for k, v in CONTROLS.items()}   # 대상오행 → 그 오행을 극하는 오행
_GENERATES_INV = {v: k for k, v in GENERATES.items()}  # 대상오행 → 그 오행을 생하는 오행

HELP_GROUPS = {"인성", "비겁"}
DRAIN_GROUPS = {"식상", "재성", "관성"}


def element_percentages(pillars: dict) -> dict:
    """4주(또는 시주 없으면 3주) 오행 분포를 %로 환산."""
    counts = count_elements(pillars)
    total = sum(counts.values())
    return {el: round(c / total * 100, 2) for el, c in counts.items()}


def element_status(count: int, total: int) -> str:
    """글자 개수 → 상태배지('부족'|'적정'|'발달'|'과다').

    8글자(시주 있음) 기준이 참조 스크린샷으로 검증됨. 6글자(시주 없음) 기준은
    참조값이 없어 동일 비례로 잠정 설정한 값이다 (§6.7 각주).
    """
    if total == 8:
        if count <= 1:
            return "부족"
        if count == 2:
            return "적정"
        if count <= 4:
            return "발달"
        return "과다"
    # 6글자
    if count <= 1:
        return "부족"
    if count == 2:
        return "적정"
    if count == 3:
        return "발달"
    return "과다"


def element_status_all(pillars: dict) -> dict:
    """오행 5개 전체의 상태배지 dict."""
    counts = count_elements(pillars)
    total = sum(counts.values())
    return {el: element_status(c, total) for el, c in counts.items()}


def _group_element_map(day_stem: str) -> dict:
    """일간 오행 기준, 십성 그룹 5개가 각각 어떤 오행에 대응하는지."""
    day_el = STEM_ELEMENT[day_stem]
    return {
        "비겁": day_el,
        "식상": GENERATES[day_el],
        "재성": CONTROLS[day_el],
        "관성": _CONTROLS_INV[day_el],
        "인성": _GENERATES_INV[day_el],
    }


def sipseong_breakdown(pillars: dict) -> dict:
    """십성 낱개 % + 그룹별(오행 대응 포함) 집계.

    반환: {'sipseong_pct': {...10개...}, 'groups': {'비겁': {'element':'목','pct':25.0}, ...}}
    """
    day_stem = pillars["day"]["stem"]
    labels: list[str] = []
    for key in ("year", "month", "day", "hour"):
        p = pillars.get(key)
        if p is None:
            continue
        labels.append("비견" if key == "day" else sipseong_of(day_stem, p["stem"]))
        labels.append(sipseong_of_branch(day_stem, p["branch"]))

    total = len(labels)
    counts = {name: 0 for name in ALL_SIPSEONG}
    for name in labels:
        counts[name] += 1
    sipseong_pct = {name: round(c / total * 100, 2) for name, c in counts.items()}

    elements_pct = element_percentages(pillars)
    group_element = _group_element_map(day_stem)
    groups = {
        group: {"element": el, "pct": elements_pct[el]}
        for group, el in group_element.items()
    }

    return {"sipseong_pct": sipseong_pct, "groups": groups}


def day_master_strength(pillars: dict) -> dict:
    """신강신약 간이 판정 (§6.8 — 참조용, 전문가 검수 전 확정 금지).

    가중치: 월지 3.0(득령) / 일지 1.5(득지) / 그 외 지지 1.0 / 월간·시간 1.0 / 년간 0.8.
    돕는 세력(인성·비겁)의 가중합 비율로 0.0~1.0 점수를 매기고 5단계로 등급화한다.
    """
    day_stem = pillars["day"]["stem"]
    has_hour = pillars.get("hour") is not None

    items: list[tuple[float, str]] = [
        (0.8, sipseong_group(sipseong_of(day_stem, pillars["year"]["stem"]))),
        (1.0, sipseong_group(sipseong_of(day_stem, pillars["month"]["stem"]))),
        (1.0, sipseong_group(sipseong_of_branch(day_stem, pillars["year"]["branch"]))),
    ]
    month_branch_group = sipseong_group(sipseong_of_branch(day_stem, pillars["month"]["branch"]))
    items.append((3.0, month_branch_group))
    day_branch_group = sipseong_group(sipseong_of_branch(day_stem, pillars["day"]["branch"]))
    items.append((1.5, day_branch_group))
    if has_hour:
        items.append((1.0, sipseong_group(sipseong_of(day_stem, pillars["hour"]["stem"]))))
        items.append((1.0, sipseong_group(sipseong_of_branch(day_stem, pillars["hour"]["branch"]))))

    total_weight = sum(w for w, _ in items)
    help_weight = sum(w for w, g in items if g in HELP_GROUPS)
    score = round(help_weight / total_weight, 4)

    if score >= 0.75:
        grade = "극신강"
    elif score >= 0.55:
        grade = "신강"
    elif score >= 0.45:
        grade = "중화"
    elif score >= 0.25:
        grade = "신약"
    else:
        grade = "극신약"

    deukse_count = sum(1 for _, g in items if g in HELP_GROUPS)

    return {
        "score": score,
        "grade": grade,
        "deukryeong": month_branch_group in HELP_GROUPS,
        "deukji": day_branch_group in HELP_GROUPS,
        "deukse": deukse_count >= 4,
    }
