"""커플 궁합 계산 검증.

일주 앵커: 2024-01-01 = 갑자(甲子)일 (KASI 표준, test_saju.py에서 검증됨).
갑자일에서 n일 뒤 = 60갑자 n칸 뒤이므로 원하는 일간·일지 조합의 날짜를 만들 수 있다.
"""

from saju import calculate_saju
from saju.compat import (
    branch_relation,
    couple_compat,
    day_stem_pair_relation,
    is_stem_hap,
    team_compat,
    zodiac_of,
)
from saju.date_neighborhoods import NEIGHBORHOODS, neighborhood_of
from saju.gapja import EARTHLY_BRANCHES, HEAVENLY_STEMS
from saju.luck import current_luck_snapshot


def _b(name):
    return EARTHLY_BRANCHES.index(name)


def _s(name):
    return HEAVENLY_STEMS.index(name)


# ── 지지 관계 판정 ────────────────────────────────────────────
def test_branch_relations():
    assert branch_relation(_b("자"), _b("축")) == "yukhap"
    assert branch_relation(_b("오"), _b("미")) == "yukhap"
    assert branch_relation(_b("자"), _b("오")) == "chung"
    assert branch_relation(_b("사"), _b("해")) == "chung"
    assert branch_relation(_b("신"), _b("자")) == "samhap"
    assert branch_relation(_b("인"), _b("술")) == "samhap"
    assert branch_relation(_b("자"), _b("미")) == "wonjin"
    assert branch_relation(_b("자"), _b("유")) is None  # 관계 없음
    assert branch_relation(_b("자"), _b("자")) is None  # 같은 지지


def test_stem_hap():
    assert is_stem_hap(_s("갑"), _s("기")) is True
    assert is_stem_hap(_s("무"), _s("계")) is True
    assert is_stem_hap(_s("갑"), _s("을")) is False


# ── 육합 커플: 갑자일(2024-01-01) + 을축일(2024-01-02) → 자축 육합 ──
def test_couple_yukhap_day_branch():
    r1 = calculate_saju(2024, 1, 1, 12, gender="male")
    r2 = calculate_saju(2024, 1, 2, 12, gender="female")
    compat = couple_compat(r1, r2)

    yukhap = [f for f in compat["factors"] if "일지 육합" in f["label"]]
    assert len(yukhap) == 1
    assert yukhap[0]["delta"] == 12
    assert compat["score"] > 50


# ── 충 커플: 갑자일 + 경오일(2024-01-07, 갑자+6) → 자오 충 ──
def test_couple_chung_day_branch():
    r1 = calculate_saju(2024, 1, 1, 12, gender="male")
    r2 = calculate_saju(2024, 1, 7, 12, gender="female")
    assert r2["pillars"]["day"]["korean"] == "경오"

    compat = couple_compat(r1, r2)
    chung = [f for f in compat["factors"] if "일지 충" in f["label"]]
    assert len(chung) == 1
    assert chung[0]["delta"] == -12


# ── 일간 천간합: 갑자일 + 기사일(2024-01-06, 갑자+5) → 갑기합 ──
def test_couple_stem_hap():
    r1 = calculate_saju(2024, 1, 1, 12, gender="male")
    r2 = calculate_saju(2024, 1, 6, 12, gender="female")
    assert r2["pillars"]["day"]["stem"] == "기"

    compat = couple_compat(r1, r2)
    hap = [f for f in compat["factors"] if "천간합" in f["label"]]
    assert len(hap) == 1
    assert hap[0]["delta"] == 15


# ── 점수 범위와 등급 ──────────────────────────────────────────
def test_score_clamped_and_graded():
    r1 = calculate_saju(2024, 1, 1, 12, gender="male")
    r2 = calculate_saju(2024, 1, 7, 12, gender="female")
    compat = couple_compat(r1, r2)
    assert 0 <= compat["score"] <= 100
    assert isinstance(compat["grade"], str) and compat["grade"]


# ── 보완 오행 (couple_compat 자체 산출물 — 지역 추천 UI는 saju/date_neighborhoods.py로 대체됨) ──
def test_complement_elements():
    r1 = calculate_saju(2024, 1, 1, 12, gender="male")
    r2 = calculate_saju(2024, 1, 2, 12, gender="female")
    compat = couple_compat(r1, r2)
    assert 1 <= len(compat["complement_elements"]) <= 2
    assert all(el in ("목", "화", "토", "금", "수") for el in compat["complement_elements"])


# ── 띠 추출 ──────────────────────────────────────────────────
def test_zodiac_of():
    r = calculate_saju(2024, 6, 1, 12, gender="male")  # 갑진년 → 용띠
    z = zodiac_of(r)
    assert z == {"branch": "진", "hanja": "辰", "animal": "용"}

    r_before_ipchun = calculate_saju(2024, 1, 1, 12, gender="male")  # 입춘 전 → 계묘년 토끼띠
    assert zodiac_of(r_before_ipchun)["animal"] == "토끼"


# ── 일간 오행 관계 (커플 데이트 화면의 生/比/剋 뱃지) ──────────────
def test_day_stem_pair_relation():
    assert day_stem_pair_relation("목", "목") == "same"
    assert day_stem_pair_relation("목", "화") == "gen"   # 목생화
    assert day_stem_pair_relation("화", "목") == "gen"   # 순서 무관
    assert day_stem_pair_relation("목", "토") == "ctrl"  # 목극토


# ── 팀(친구 3~4인) 궁합: 쌍별 couple_compat 평균과 일치해야 한다 ──
def test_team_compat_matches_pairwise_average():
    r1 = calculate_saju(2024, 1, 1, 12, gender="male")     # 갑자일
    r2 = calculate_saju(2024, 1, 2, 12, gender="female")   # 을축일 (자축 육합)
    r3 = calculate_saju(2024, 1, 7, 12, gender="male")     # 경오일 (자오 충)

    team = team_compat([r1, r2, r3])
    expected = [couple_compat(r1, r2)["score"], couple_compat(r1, r3)["score"], couple_compat(r2, r3)["score"]]
    assert team["score"] == round(sum(expected) / 3)
    assert len(team["pairwise"]) == 3
    assert isinstance(team["grade"], str) and team["grade"]


def test_team_compat_requires_at_least_two():
    import pytest
    with pytest.raises(ValueError):
        team_compat([calculate_saju(2024, 1, 1, 12, gender="male")])


# ── 지금 이 순간의 세운·월운 스냅샷 ────────────────────────────
def test_current_luck_snapshot_matches_direct_calculation():
    from datetime import datetime

    from saju.pillars import month_pillar, year_pillar

    now = datetime(2026, 7, 13, 12, 0)
    snap = current_luck_snapshot(now)

    yp = year_pillar(now)
    mp = month_pillar(now, HEAVENLY_STEMS.index(yp["stem"]))
    assert snap["seun"]["hanja"] == yp["hanja"]
    assert snap["wolun"]["hanja"] == mp["hanja"]
    assert "branch_element" in snap["wolun"]


# ── 이 달의 데이트 동네 (오행 → 동네 1곳 + 폴백 장소) ──────────────
def test_neighborhood_of_covers_all_elements():
    for element in ("목", "화", "토", "금", "수"):
        nbh = neighborhood_of(element)
        assert nbh["element"] == element
        assert nbh["name"] and nbh["tag"] and nbh["why"]
        assert len(nbh["places"]) >= 1
        for place in nbh["places"]:
            assert place["name"] and place["category"] and place["address"]


def test_neighborhoods_have_exactly_five_elements():
    assert set(NEIGHBORHOODS.keys()) == {"목", "화", "토", "금", "수"}
