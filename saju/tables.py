"""지장간(藏干)·납음오행(納音五行)·오행(五行) 통계 조회."""

from __future__ import annotations

from .gapja import BRANCH_ELEMENT, STEM_ELEMENT, gapja_index

# 지지별 지장간(여기·중기·정기 순). 자/묘/유는 2개, 나머지는 3개.
HIDDEN_STEMS = {
    "자": ["임", "계"],
    "축": ["계", "신", "기"],
    "인": ["무", "병", "갑"],
    "묘": ["갑", "을"],
    "진": ["을", "계", "무"],
    "사": ["무", "경", "병"],
    "오": ["병", "기", "정"],
    "미": ["정", "을", "기"],
    "신": ["무", "임", "경"],
    "유": ["경", "신"],
    "술": ["신", "정", "무"],
    "해": ["무", "갑", "임"],
}

# 60갑자를 2개씩 묶은 납음오행 30항목(순서 = 갑자 인덱스 // 2).
NAYIN_NAMES = [
    ("해중금", "海中金"), ("노중화", "爐中火"), ("대림목", "大林木"), ("노방토", "路傍土"),
    ("검봉금", "劍鋒金"), ("산두화", "山頭火"), ("간하수", "澗下水"), ("성두토", "城頭土"),
    ("백랍금", "白蠟金"), ("양류목", "楊柳木"), ("천중수", "泉中水"), ("옥상토", "屋上土"),
    ("벽력화", "霹靂火"), ("송백목", "松柏木"), ("장류수", "長流水"), ("사중금", "沙中金"),
    ("산하화", "山下火"), ("평지목", "平地木"), ("벽상토", "壁上土"), ("금박금", "金箔金"),
    ("복등화", "覆燈火"), ("천하수", "天河水"), ("대역토", "大驛土"), ("차천금", "釵釧金"),
    ("상자목", "桑柘木"), ("대계수", "大溪水"), ("사중토", "沙中土"), ("천상화", "天上火"),
    ("석류목", "石榴木"), ("대해수", "大海水"),
]


def hidden_stems(branch: str) -> list[str]:
    """지지 한 글자의 지장간(2~3개) 목록."""
    return HIDDEN_STEMS[branch]


def nayin_of(stem_idx: int, branch_idx: int) -> dict:
    """(천간 인덱스, 지지 인덱스) → 납음오행 {'korean', 'hanja'}."""
    korean, hanja = NAYIN_NAMES[gapja_index(stem_idx, branch_idx) // 2]
    return {"korean": korean, "hanja": hanja}


def count_elements(pillars: dict) -> dict:
    """4주(년/월/일/시) 천간·지지의 오행 개수. 시주가 없으면(None) 6글자만 집계."""
    counts = {"목": 0, "화": 0, "토": 0, "금": 0, "수": 0}
    for key in ("year", "month", "day", "hour"):
        p = pillars.get(key)
        if p is None:
            continue
        counts[STEM_ELEMENT[p["stem"]]] += 1
        counts[BRANCH_ELEMENT[p["branch"]]] += 1
    return counts
