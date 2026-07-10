"""60갑자(干支) 공용 상수와 유틸리티."""

from __future__ import annotations

HEAVENLY_STEMS = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
EARTHLY_BRANCHES = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]

STEMS_HANJA = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES_HANJA = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 지지 순서와 동일한 띠 동물
BRANCH_ANIMALS = ["쥐", "소", "호랑이", "토끼", "용", "뱀", "말", "양", "원숭이", "닭", "개", "돼지"]

# 천간/지지 오행(五行). 대운 순행/역행 판정에 쓰이는 연간 음양은 stem_idx % 2로 구한다
# (0,2,4,6,8=양간, 1,3,5,7,9=음간).
STEM_ELEMENT = {
    "갑": "목", "을": "목",
    "병": "화", "정": "화",
    "무": "토", "기": "토",
    "경": "금", "신": "금",
    "임": "수", "계": "수",
}
BRANCH_ELEMENT = {
    "자": "수", "해": "수",
    "인": "목", "묘": "목",
    "사": "화", "오": "화",
    "신": "금", "유": "금",
    "축": "토", "진": "토", "미": "토", "술": "토",
}


def pillar(stem_idx: int, branch_idx: int) -> dict:
    stem_idx %= 10
    branch_idx %= 12
    stem = HEAVENLY_STEMS[stem_idx]
    branch = EARTHLY_BRANCHES[branch_idx]
    return {
        "stem": stem,
        "branch": branch,
        "hanja": STEMS_HANJA[stem_idx] + BRANCHES_HANJA[branch_idx],
        "korean": stem + branch,
        "stem_element": STEM_ELEMENT[stem],
        "branch_element": BRANCH_ELEMENT[branch],
    }


def gapja_index(stem_idx: int, branch_idx: int) -> int:
    """(천간 인덱스, 지지 인덱스) → 60갑자 순번(0~59, 0=갑자)."""
    stem_idx %= 10
    branch_idx %= 12
    for i in range(60):
        if i % 10 == stem_idx and i % 12 == branch_idx:
            return i
    raise ValueError("갑자 인덱스 산출 실패")  # pragma: no cover — 수학적으로 도달 불가
