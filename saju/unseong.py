"""12운성(十二運星) 판정. plan/active/05-saju-analysis-engine.md §6.2.

양생음사(陽生陰死) 정통설 채택: 양간은 순행, 음간은 역행.
화토동법(무=인, 기=유) 채택 — 수토동법 등 대안은 plan 문서 §11 참고.
"""

from __future__ import annotations

from .gapja import EARTHLY_BRANCHES
from .tables_analysis import UNSEONG12_ANCHOR, UNSEONG12_ORDER


def unseong12_of(day_stem: str, branch: str) -> str:
    """일간이 해당 지지에서 갖는 12운성 단계."""
    anchor_branch, forward = UNSEONG12_ANCHOR[day_stem]
    anchor_idx = EARTHLY_BRANCHES.index(anchor_branch)
    target_idx = EARTHLY_BRANCHES.index(branch)
    offset = (target_idx - anchor_idx) % 12 if forward else (anchor_idx - target_idx) % 12
    return UNSEONG12_ORDER[offset]
