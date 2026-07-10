"""지장간·납음오행·오행 통계·대운·세운 계산 검증.

지장간·납음오행·오행 통계 앵커는 사용자가 제공한 실제 만세력 앱 스크린샷
(년주 丙寅/월주 丙申/일주 癸卯/시주 戊午, 대운수:4 순행, 세운 2024=甲辰)과 대조했다.
"""

from datetime import datetime

from saju.gapja import EARTHLY_BRANCHES, HEAVENLY_STEMS, pillar
from saju.luck import daewoon_pillars, is_forward, seun_pillars
from saju.tables import count_elements, hidden_stems, nayin_of


def _idx(stem, branch):
    return HEAVENLY_STEMS.index(stem), EARTHLY_BRANCHES.index(branch)


# ── 지장간 ────────────────────────────────────────────────────
def test_hidden_stems_known_branches():
    assert hidden_stems("오") == ["병", "기", "정"]
    assert hidden_stems("묘") == ["갑", "을"]
    assert hidden_stems("신") == ["무", "임", "경"]
    assert hidden_stems("인") == ["무", "병", "갑"]


# ── 납음오행 (스크린샷 4주 앵커) ────────────────────────────────
def test_nayin_matches_reference_screenshot():
    assert nayin_of(*_idx("무", "오"))["korean"] == "천상화"
    assert nayin_of(*_idx("계", "묘"))["korean"] == "금박금"
    assert nayin_of(*_idx("병", "신"))["korean"] == "산하화"
    assert nayin_of(*_idx("병", "인"))["korean"] == "노중화"


# ── 오행 개수 ─────────────────────────────────────────────────
def test_count_elements_matches_reference_screenshot():
    pillars = {
        "year": pillar(*_idx("병", "인")),
        "month": pillar(*_idx("병", "신")),
        "day": pillar(*_idx("계", "묘")),
        "hour": pillar(*_idx("무", "오")),
    }
    assert count_elements(pillars) == {"목": 2, "화": 3, "토": 1, "금": 1, "수": 1}


def test_count_elements_ignores_missing_hour():
    pillars = {
        "year": pillar(*_idx("병", "인")),
        "month": pillar(*_idx("병", "신")),
        "day": pillar(*_idx("계", "묘")),
        "hour": None,
    }
    counts = count_elements(pillars)
    assert sum(counts.values()) == 6
    assert counts["화"] == 2  # 병(년), 병(월)


# ── 대운 순행/역행 판정 ────────────────────────────────────────
def test_is_forward_rules():
    gap_idx = HEAVENLY_STEMS.index("갑")  # 양간
    eul_idx = HEAVENLY_STEMS.index("을")  # 음간
    assert is_forward(gap_idx, "male") is True
    assert is_forward(gap_idx, "female") is False
    assert is_forward(eul_idx, "male") is False
    assert is_forward(eul_idx, "female") is True


# ── 대운 리스트 (스크린샷 대운 시퀀스와 대조) ────────────────────
def test_daewoon_sequence_matches_reference_screenshot():
    """월주 丙申 기준 순행 대운: 丁酉,戊戌,己亥,庚子,辛丑,壬寅,癸卯,甲辰,乙巳 (스크린샷과 일치)."""
    dt = datetime(1986, 8, 20, 12, 0)
    month_stem_idx, month_branch_idx = _idx("병", "신")
    result = daewoon_pillars(dt, month_stem_idx, month_branch_idx, "male")

    assert result["direction"] == "순행"
    hanja_sequence = [p["hanja"] for p in result["pillars"][:9]]
    assert hanja_sequence == [
        "丁酉", "戊戌", "己亥", "庚子", "辛丑", "壬寅", "癸卯", "甲辰", "乙巳",
    ]
    ages = [p["age"] for p in result["pillars"][:3]]
    assert ages[1] - ages[0] == 10
    assert ages[2] - ages[1] == 10


def test_daewoon_backward_direction():
    dt = datetime(1986, 8, 20, 12, 0)
    month_stem_idx, month_branch_idx = _idx("병", "신")
    result = daewoon_pillars(dt, month_stem_idx, month_branch_idx, "female")
    assert result["direction"] == "역행"
    # 역행이면 월주(丙申)에서 거꾸로: 乙未, 甲午, ...
    assert result["pillars"][0]["hanja"] == "乙未"


# ── 세운 (스크린샷 2024=甲辰과 대조) ─────────────────────────────
def test_seun_matches_reference_screenshot():
    result = seun_pillars(center_year=2024, span=4)
    by_year = {p["year"]: p["hanja"] for p in result}
    assert by_year[2024] == "甲辰"
    assert len(result) == 9
