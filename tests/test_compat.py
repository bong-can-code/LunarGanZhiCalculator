"""커플 궁합 계산 검증.

일주 앵커: 2024-01-01 = 갑자(甲子)일 (KASI 표준, test_saju.py에서 검증됨).
갑자일에서 n일 뒤 = 60갑자 n칸 뒤이므로 원하는 일간·일지 조합의 날짜를 만들 수 있다.
"""

from saju import calculate_saju
from saju.compat import branch_relation, couple_compat, is_stem_hap, zodiac_of
from saju.gapja import EARTHLY_BRANCHES, HEAVENLY_STEMS
from saju.regions import DISTRICT_SPOTS, ELEMENT_DISTRICTS, recommend_districts


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


# ── 보완 오행과 지역 추천 ─────────────────────────────────────
def test_complement_elements_and_districts():
    r1 = calculate_saju(2024, 1, 1, 12, gender="male")
    r2 = calculate_saju(2024, 1, 2, 12, gender="female")
    compat = couple_compat(r1, r2)

    assert 1 <= len(compat["complement_elements"]) <= 2

    rec = recommend_districts(compat["complement_elements"])
    assert rec["districts"], "추천 지역이 비어 있으면 안 된다"
    for d in rec["districts"]:
        assert d["name"] in DISTRICT_SPOTS
        assert len(d["spots"]) >= 1


def test_all_mapped_districts_have_spots():
    """오행 매핑에 등장하는 모든 구는 폴백 명소를 가져야 한다."""
    for districts in ELEMENT_DISTRICTS.values():
        for name in districts:
            assert name in DISTRICT_SPOTS, f"{name} 폴백 명소 누락"


# ── 띠 추출 ──────────────────────────────────────────────────
def test_zodiac_of():
    r = calculate_saju(2024, 6, 1, 12, gender="male")  # 갑진년 → 용띠
    z = zodiac_of(r)
    assert z == {"branch": "진", "hanja": "辰", "animal": "용"}

    r_before_ipchun = calculate_saju(2024, 1, 1, 12, gender="male")  # 입춘 전 → 계묘년 토끼띠
    assert zodiac_of(r_before_ipchun)["animal"] == "토끼"
