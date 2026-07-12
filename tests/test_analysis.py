"""명리 분석 엔진(십성·12운성·12신살·공망·신살길성·합충형파해·오행%·신강신약) 검증.

골든 케이스: 1995-10-10 13시생(미시) 남성, 양력.
  → 년주 乙亥, 월주 丙戌, 일주 甲戌, 시주 辛未
사용자가 제공한 참조 만세력 앱 스크린샷(2026-07)의 표시값과 전부 대조했다.
날짜 확정 방법: korean-lunar-calendar로 1995년 10~11월 구간에서 갑술일(甲戌日)을
탐색해 유일 후보를 찾고, 우리 calculate_saju()로 4주가 정확히 일치함을 확인했다
(plan/active/05-saju-analysis-engine.md §4 참고).
"""

from __future__ import annotations

import pytest

from saju import calculate_saju
from saju.gapja import EARTHLY_BRANCHES, HEAVENLY_STEMS
from saju.relations import branch_relations, stem_relations
from saju.sinsal import gilseong_of, gongmang_of, sinsal12_of
from saju.sipseong import sipseong_group, sipseong_of, sipseong_of_branch
from saju.strength import (
    day_master_strength,
    element_percentages,
    element_status_all,
    sipseong_breakdown,
)
from saju.unseong import unseong12_of


@pytest.fixture(scope="module")
def golden():
    """1995-10-10 13시(미시) 남성 — 년乙亥 월丙戌 일甲戌 시辛未."""
    return calculate_saju(1995, 10, 10, 13, gender="male")


def test_golden_pillars_sanity(golden):
    """분석 테스트의 전제인 4주 자체가 스크린샷과 일치하는지 먼저 확인."""
    p = golden["pillars"]
    assert p["year"]["hanja"] == "乙亥"
    assert p["month"]["hanja"] == "丙戌"
    assert p["day"]["hanja"] == "甲戌"
    assert p["hour"]["hanja"] == "辛未"


# ── 십성 (§6.1) ──────────────────────────────────────────────
def test_sipseong_of_stem_matches_screenshot(golden):
    day_stem = golden["pillars"]["day"]["stem"]  # 갑
    assert sipseong_of(day_stem, golden["pillars"]["hour"]["stem"]) == "정관"   # 辛
    assert sipseong_of(day_stem, golden["pillars"]["month"]["stem"]) == "식신"  # 丙
    assert sipseong_of(day_stem, golden["pillars"]["year"]["stem"]) == "겁재"   # 乙
    # sipseong_of()는 순수 계산만 하므로 일간 자신도 실제 십성(비견)을 반환한다.
    # '일원' 표시 라벨은 calculator._enrich가 일주 자리에서만 덧씌운다 (§6.1).
    assert sipseong_of(day_stem, day_stem) == "비견"                            # 甲


def test_sipseong_of_branch_matches_screenshot(golden):
    day_stem = golden["pillars"]["day"]["stem"]
    assert sipseong_of_branch(day_stem, golden["pillars"]["hour"]["branch"]) == "정재"  # 未
    assert sipseong_of_branch(day_stem, golden["pillars"]["day"]["branch"]) == "편재"   # 戌(일지)
    assert sipseong_of_branch(day_stem, golden["pillars"]["month"]["branch"]) == "편재"  # 戌(월지)
    assert sipseong_of_branch(day_stem, golden["pillars"]["year"]["branch"]) == "편인"   # 亥


def test_sipseong_of_daewoon_and_seun_columns(golden):
    """대운(만) 스크린샷 40/30/20/10/0세 컬럼 십성과 대조."""
    day_stem = golden["pillars"]["day"]["stem"]
    cases = [
        ("신", "사", "정관", "식신"),  # 40세: 辛巳
        ("임", "오", "편인", "상관"),  # 30세: 壬午
        ("계", "미", "정인", "정재"),  # 20세: 癸未
        ("갑", "신", "비견", "편관"),  # 10세: 甲申
        ("을", "유", "겁재", "정관"),  #  0세: 乙酉
    ]
    for stem, branch, expected_stem_sipseong, expected_branch_sipseong in cases:
        assert sipseong_of(day_stem, stem) == expected_stem_sipseong
        assert sipseong_of_branch(day_stem, branch) == expected_branch_sipseong


def test_sipseong_group():
    assert sipseong_group("비견") == "비겁"
    assert sipseong_group("겁재") == "비겁"
    assert sipseong_group("식신") == "식상"
    assert sipseong_group("정관") == "관성"
    assert sipseong_group("일원") == "비겁"


# ── 12운성 (§6.2) ────────────────────────────────────────────
def test_unseong12_matches_screenshot_wongook(golden):
    day_stem = golden["pillars"]["day"]["stem"]
    assert unseong12_of(day_stem, golden["pillars"]["hour"]["branch"]) == "묘"   # 未
    assert unseong12_of(day_stem, golden["pillars"]["day"]["branch"]) == "양"    # 戌(일지)
    assert unseong12_of(day_stem, golden["pillars"]["month"]["branch"]) == "양"  # 戌(월지)
    assert unseong12_of(day_stem, golden["pillars"]["year"]["branch"]) == "장생"  # 亥


def test_unseong12_matches_screenshot_daewoon(golden):
    day_stem = golden["pillars"]["day"]["stem"]
    assert unseong12_of(day_stem, "사") == "병"   # 40세 대운 巳
    assert unseong12_of(day_stem, "오") == "사"   # 30세 대운 午
    assert unseong12_of(day_stem, "미") == "묘"   # 20세 대운 未
    assert unseong12_of(day_stem, "신") == "절"   # 10세 대운 申
    assert unseong12_of(day_stem, "유") == "태"   #  0세 대운 酉


# ── 12신살 (§6.3, 원국표 = 년지 기준) ───────────────────────────
def test_sinsal12_matches_screenshot(golden):
    year_branch = golden["pillars"]["year"]["branch"]  # 해
    assert sinsal12_of(year_branch, golden["pillars"]["hour"]["branch"]) == "화개살"  # 未
    assert sinsal12_of(year_branch, golden["pillars"]["day"]["branch"]) == "천살"    # 戌(일지)
    assert sinsal12_of(year_branch, golden["pillars"]["month"]["branch"]) == "천살"  # 戌(월지)
    assert sinsal12_of(year_branch, year_branch) == "지살"                          # 亥(년지)


# ── 공망 (§6.4) ──────────────────────────────────────────────
def test_gongmang_matches_screenshot(golden):
    day_stem_idx = HEAVENLY_STEMS.index(golden["pillars"]["day"]["stem"])
    day_branch_idx = EARTHLY_BRANCHES.index(golden["pillars"]["day"]["branch"])
    assert set(gongmang_of(day_stem_idx, day_branch_idx)) == {"신", "유"}


# ── 신살/길성 (§6.5) ─────────────────────────────────────────
def test_gilseong_matches_screenshot(golden):
    p = golden["pillars"]
    pillars_in = {
        "year": {"stem": p["year"]["stem"], "branch": p["year"]["branch"]},
        "month": {"stem": p["month"]["stem"], "branch": p["month"]["branch"]},
        "day": {"stem": p["day"]["stem"], "branch": p["day"]["branch"]},
        "hour": {"stem": p["hour"]["stem"], "branch": p["hour"]["branch"]},
    }
    g = gilseong_of(pillars_in)

    # 천간: 시辛=현침살, 일甲=현침살, 월丙=천덕+월덕+백호대살, 년乙=없음
    assert g["stems"]["hour"] == ["현침살"]
    assert g["stems"]["day"] == ["현침살"]
    assert set(g["stems"]["month"]) == {"천덕귀인", "월덕귀인", "백호대살"}
    assert g["stems"]["year"] == []

    # 지지: 시未=천을귀인+화개살, 일戌=급각살+화개살, 월戌=백호대살+화개살, 년亥=문곡+학당+암록
    assert set(g["branches"]["hour"]) == {"천을귀인", "화개살"}
    assert set(g["branches"]["day"]) == {"급각살", "화개살"}
    assert set(g["branches"]["month"]) == {"백호대살", "화개살"}
    assert set(g["branches"]["year"]) == {"문곡귀인", "학당귀인", "암록"}


def test_gilseong_handles_missing_hour():
    """시간 모름(hour=None)이어도 나머지 3주는 정상 계산되어야 한다."""
    r = calculate_saju(1995, 10, 10, None, gender="male")
    p = r["pillars"]
    pillars_in = {
        "year": {"stem": p["year"]["stem"], "branch": p["year"]["branch"]},
        "month": {"stem": p["month"]["stem"], "branch": p["month"]["branch"]},
        "day": {"stem": p["day"]["stem"], "branch": p["day"]["branch"]},
        "hour": None,
    }
    g = gilseong_of(pillars_in)
    assert g["stems"]["hour"] == []
    assert g["branches"]["hour"] == []
    assert set(g["stems"]["month"]) == {"천덕귀인", "월덕귀인", "백호대살"}


# ── 오행 % · 십성그룹 · 상태배지 (§6.7) ──────────────────────
def test_element_percentages_matches_screenshot(golden):
    pct = element_percentages(golden["pillars"])
    assert pct == {"목": 25.0, "화": 12.5, "토": 37.5, "금": 12.5, "수": 12.5}


def test_element_status_matches_screenshot(golden):
    status = element_status_all(golden["pillars"])
    assert status == {"목": "적정", "화": "부족", "토": "발달", "금": "부족", "수": "부족"}


def test_sipseong_breakdown_matches_screenshot(golden):
    breakdown = sipseong_breakdown(golden["pillars"])
    pct = breakdown["sipseong_pct"]
    assert pct["비견"] == 12.5
    assert pct["겁재"] == 12.5
    assert pct["식신"] == 12.5
    assert pct["상관"] == 0.0
    assert pct["편재"] == 25.0
    assert pct["정재"] == 12.5
    assert pct["편관"] == 0.0
    assert pct["정관"] == 12.5
    assert pct["편인"] == 12.5
    assert pct["정인"] == 0.0

    groups = breakdown["groups"]
    assert groups["비겁"] == {"element": "목", "pct": 25.0}
    assert groups["식상"] == {"element": "화", "pct": 12.5}
    assert groups["재성"] == {"element": "토", "pct": 37.5}
    assert groups["관성"] == {"element": "금", "pct": 12.5}
    assert groups["인성"] == {"element": "수", "pct": 12.5}


# ── 합충형파해 (§6.6) — 표 자체의 대표 케이스(위키백과 표준) ─────
def test_branch_relations_known_cases():
    rel = branch_relations({"year": "자", "month": "축", "day": "오", "hour": None})
    kinds = {r["kind"] for r in rel}
    assert "육합" in kinds  # 자축
    assert "충" in kinds    # 자오


def test_branch_relations_full_samhap_vs_banhap():
    full = branch_relations({"year": "신", "month": "자", "day": "진", "hour": None})
    assert any(r["kind"] == "삼합" for r in full)  # 신자진 전체 존재

    partial = branch_relations({"year": "신", "month": "자", "day": "오", "hour": None})
    assert any(r["kind"] == "반삼합" for r in partial)  # 신자만 존재(진 없음)


def test_stem_relations_known_cases():
    rel = stem_relations({"year": "갑", "month": "기", "day": "병", "hour": "임"})
    kinds = {(r["kind"], tuple(r["chars"])) for r in rel}
    assert ("천간합", ("갑", "기")) in kinds
    assert ("천간충", ("병", "임")) in kinds


# ── 신강신약 (§6.8) — 참조용 간이 판정, 실행 자체만 검증 ─────────
def test_day_master_strength_runs_and_shapes(golden):
    result = day_master_strength(golden["pillars"])
    assert 0.0 <= result["score"] <= 1.0
    assert result["grade"] in ("극신강", "신강", "중화", "신약", "극신약")
    assert isinstance(result["deukryeong"], bool)
    assert isinstance(result["deukji"], bool)
    assert isinstance(result["deukse"], bool)


# ── 통합 API(calculate_saju) 자체가 §7 스펙대로 노출하는지 ────────
def test_calculate_saju_exposes_analysis_fields(golden):
    assert golden["day_master"] == {
        "stem": "갑", "hanja": "甲", "element": "목", "yin_yang": "양",
    }
    assert set(golden["gongmang"]) == {"신", "유"}

    day_p = golden["pillars"]["day"]
    assert day_p["sipseong_stem"] == "일원"       # 통계용이 아닌 표시 라벨
    assert day_p["yin_yang_stem"] == "양"          # 甲
    assert day_p["yin_yang_branch"] == "양"        # 戌
    assert day_p["unseong12"] == "양"
    assert day_p["sinsal12"] == "천살"
    assert day_p["is_gongmang"] is False

    hour_p = golden["pillars"]["hour"]
    assert hour_p["sipseong_stem"] == "정관"
    assert hour_p["sipseong_branch"] == "정재"
    assert hour_p["unseong12"] == "묘"
    assert hour_p["sinsal12"] == "화개살"

    assert golden["analysis"]["elements_pct"]["토"] == 37.5
    assert golden["analysis"]["groups"]["재성"] == {"element": "토", "pct": 37.5}

    month_stems = golden["gilseong"]["stems"]["month"]
    assert set(month_stems) == {"천덕귀인", "월덕귀인", "백호대살"}


def test_calculate_saju_daewoon_seun_have_sipseong_unseong_labels(golden):
    """辛巳 대운(스크린샷 40세 컬럼)이 동일한 십성·12운성 라벨을 갖는지.

    골든 픽스처의 실제 대운수는 1(§11 '대운 나이' 유파차로 스크린샷의 0과 다름)이라
    나이 숫자 대신 간지(辛巳)로 해당 컬럼을 찾는다 — 나이 규칙과 무관하게
    라벨링 로직 자체를 검증하는 것이 이 테스트의 목적이다.
    """
    p_sinsa = next(p for p in golden["daewoon"]["pillars"] if p["hanja"] == "辛巳")
    assert p_sinsa["sipseong_stem"] == "정관"
    assert p_sinsa["sipseong_branch"] == "식신"
    assert p_sinsa["unseong12"] == "병"


def test_seun_labels_use_luck_analysis_helper():
    """세운 라벨링이 실제 calculator 파이프라인과 동일한 헬퍼로 붙는지 (2024=甲辰 고정 간지 기준)."""
    from saju.calculator import _add_luck_analysis
    from saju.luck import seun_pillars

    items = _add_luck_analysis(seun_pillars(center_year=2024, span=0), day_stem="갑")
    assert len(items) == 1
    s2024 = items[0]
    assert s2024["hanja"] == "甲辰"
    assert s2024["sipseong_stem"] == "비견"
    assert s2024["sipseong_branch"] == "편재"
    assert s2024["unseong12"] == "쇠"


def test_calculate_saju_no_hour_pillar_analysis_is_empty():
    r = calculate_saju(1995, 10, 10, None, gender="male")
    assert r["pillars"]["hour"] is None
    assert r["gilseong"]["stems"]["hour"] == []
    assert r["gilseong"]["branches"]["hour"] == []
    assert isinstance(r["relations"]["stems"], list)
    assert isinstance(r["relations"]["branches"], list)
