"""십성(十星, 십신) 판정. plan/active/05-saju-analysis-engine.md §6.1."""

from __future__ import annotations

from .gapja import HEAVENLY_STEMS, STEM_ELEMENT
from .tables import HIDDEN_STEMS
from .tables_analysis import CONTROLS, GENERATES

# (같은 오행, 일간이 생, 일간이 극, 대상이 극, 대상이 생) → (같은 음양 이름, 다른 음양 이름)
_GROUP_NAMES = {
    "비겁": ("비견", "겁재"),
    "식상": ("식신", "상관"),
    "재성": ("편재", "정재"),
    "관성": ("편관", "정관"),
    "인성": ("편인", "정인"),
}


def sipseong_group_of(day_stem: str, target_stem: str) -> str:
    """일간과 대상 천간의 오행 관계로 십성 그룹('비겁'|'식상'|'재성'|'관성'|'인성')을 판정."""
    day_el = STEM_ELEMENT[day_stem]
    target_el = STEM_ELEMENT[target_stem]
    if day_el == target_el:
        return "비겁"
    if GENERATES[day_el] == target_el:
        return "식상"
    if CONTROLS[day_el] == target_el:
        return "재성"
    if CONTROLS[target_el] == day_el:
        return "관성"
    return "인성"  # GENERATES[target_el] == day_el (오행 5개는 이 5가지 관계로 전부 커버됨)


def sipseong_of(day_stem: str, target_stem: str) -> str:
    """일간 기준 천간 하나의 십성('비견'~'정인').

    일간과 같은 글자라도(대운·세운에 우연히 같은 천간이 다시 나오는 경우 등) 항상
    실제 십성 이름(비견)을 반환한다. '일원' 표시는 사주원국 "일주 자리" 전용
    디스플레이 라벨이라 계산 계층이 아니라 호출부(calculator._enrich)에서만 붙인다
    (plan 05 §6.1: "통계 집계상 비견").
    """
    group = sipseong_group_of(day_stem, target_stem)
    same_yang = (HEAVENLY_STEMS.index(day_stem) % 2) == (HEAVENLY_STEMS.index(target_stem) % 2)
    same_name, diff_name = _GROUP_NAMES[group]
    return same_name if same_yang else diff_name


def sipseong_of_branch(day_stem: str, branch: str) -> str:
    """지지의 십성. 지장간 본기(정기 = 마지막 원소) 천간을 기준으로 판정한다."""
    bon_gi = HIDDEN_STEMS[branch][-1]
    return sipseong_of(day_stem, bon_gi)


def sipseong_group(sipseong: str) -> str:
    """십성 낱개 이름('비견' 등) → 그룹 이름('비겁' 등). '일원'은 '비겁'으로 취급."""
    if sipseong == "일원":
        return "비겁"
    for group, (same_name, diff_name) in _GROUP_NAMES.items():
        if sipseong in (same_name, diff_name):
            return group
    raise ValueError(f"알 수 없는 십성: {sipseong}")  # pragma: no cover — 호출부에서 유효값만 전달
