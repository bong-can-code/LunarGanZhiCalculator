# ssod-saju-engine (소디사주엔진)

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)

생년월일시를 입력받아 **사주(四柱) 간지(干支)와 명리(命理) 지표를 계산하는
순수 Python 엔진**입니다. 양력/음력 입력을 모두 지원하며, 연·월·일·시 4주의
간지, 대운/세운, 십성·12운성·12신살·공망·신살/길성·합충형파해·오행 통계·궁합까지
계산합니다. UI·웹 프레임워크 의존성이 없어 라이브러리로 임베드하거나
동봉된 참조 HTTP API 서버로 띄워 언어 무관하게 사용할 수 있습니다.

> 이 레포는 **계산 엔진(오픈소스)** 입니다. 웹 UI·콘텐츠·수익화 등 서비스 레이어는
> 별도 비공개 레포에서 이 엔진을 의존해 구성합니다.

## 설치

```bash
pip install ssod-saju-engine        # (PyPI 배포 후)
# 또는 개발 중:
pip install git+https://github.com/qbong1010/LunarGanZhiCalculator.git
```

의존성은 `korean-lunar-calendar`(음↔양력 변환, MIT) 하나뿐입니다.

## 사용법

```python
from saju import calculate_saju

result = calculate_saju(
    1990, 5, 15, hour=14,        # 양력 1990-05-15 14시
    is_lunar=False,              # 음력이면 True (윤달은 is_leap_month=True)
    gender="male",               # 주어지면 대운(순행/역행·대운수)도 계산
)

print(result["pillars"]["day"]["korean"])   # 일주 간지 (예: '경오')
print(result["day_master"])                 # 일간(오행·음양)
print(result["elements"])                   # 오행 개수 통계
print(result["analysis"]["strength"])       # 신강신약(참고용 간이 점수)
print(result["daewoon"])                    # 대운 리스트
```

반환 dict의 최상위 키: `solar`, `lunar`, `pillars`, `elements`, `daewoon`,
`seun`, `day_master`, `gongmang`, `gilseong`, `relations`, `analysis`.

### 궁합

```python
from saju import calculate_saju
from saju.compat import couple_compat, team_compat

a = calculate_saju(1990, 5, 15, 14, gender="male")
b = calculate_saju(1992, 8, 3, 9, gender="female")
print(couple_compat(a, b))          # 2인 궁합 점수·등급·요인
print(team_compat([a, b, ...]))     # 3~4인 팀 궁합
```

## 참조 HTTP API 서버

`server/`에 엔진을 그대로 노출하는 얇은 FastAPI 래퍼가 있습니다(OpenAPI 문서 자동 생성).

```bash
pip install "ssod-saju-engine[server]"
uvicorn server.main:app --reload      # http://127.0.0.1:8000/docs
```

## 📐 계산 기준 (정확도 근거)

정통 명리학 기준을 따릅니다 ([saju/pillars.py](saju/pillars.py)).

| 기둥 | 기준 |
|------|------|
| 연주(年柱) | **입춘(立春)** 절입시각을 연 경계로 삼습니다. 입춘 이전 출생은 전년도 간지. |
| 월주(月柱) | 음력 월이 아니라 **12절(節)** 로 월 경계를 잡고, 연간에 **오호둔(五虎遁)** 적용. |
| 일주(日柱) | 60갑자 순환. `korean-lunar-calendar`(KASI 표준)의 일간지를 외부 앵커(1949-10-01, 2024-01-01 갑자일)로 교차검증. |
| 시주(時柱) | **정자시(23:00 날짜 전환)** 기준, 일간에 **오서둔(五鼠遁)** 적용. |

대운·세운은 [saju/luck.py](saju/luck.py)에서 계산합니다:

| 항목 | 기준 |
|------|------|
| 순행/역행 | 연간의 음양 × 성별. 양간+남자 또는 음간+여자 → 순행, 반대는 역행. |
| 대운수 | 다음 절(순행)/직전 절(역행)까지 일수를 3으로 나눔("3일=1년", 최소 1). |
| 대운 간지 | 월주 기준 순행이면 다음 갑자, 역행이면 이전 갑자로 10년마다 진행. |
| 세운 | 그 해 대표 시점(6월 1일)의 연주. 현재 연도 중심 앞뒤 4년. |

### 🧮 명리 분석 기준 (십성·12운성·12신살·신강신약 등)

상세 룰 테이블은 [plan/active/05-saju-analysis-engine.md](plan/active/05-saju-analysis-engine.md) §6,
전문가 검수용 요약은 [docs/expert-review/saju-analysis-rules.md](docs/expert-review/saju-analysis-rules.md) 참고.

| 항목 | 기준 |
|------|------|
| 십성(十星) | 일간과 대상 오행의 생극 × 음양 일치. 지지 십성은 지장간 **본기**(정기) 기준. |
| 12운성 | **양생음사**(양간 순행·음간 역행), 화토동법(무=인, 기=유). |
| 12신살 | 원국·대운·세운 모두 **년지** 기준, 삼합국 겁살부터 순환. |
| 공망(空亡) | 일주의 순중공망 — 60갑자 순에서 비는 지지 2개. |
| 신강신약 | **참고용 간이 점수제**(월지 3.0·일지 1.5 가중). 격국·조후 반영 정통 판정과 다를 수 있음. |

### ⚠️ 제한 사항

- **야자시/조자시 미채택**: 23시 이후를 다음날로 보는 정자시설 채택. 야자시 유파와 다를 수 있음.
- **절기 시각**: [saju/solar_terms.py](saju/solar_terms.py) 천문 계산식 사용, 연도별 분 단위 오차 가능.
- **대운수 반올림**: 파이썬 기본 반올림(banker's rounding). 경계값에서 ±1세 차이 가능.
- **신강신약은 참고용**, **사주 해석 없음**: 간지·오행 통계·명리 지표까지만. 용신·격국 등 심층 해석은 범위 밖.

## 개발

```bash
pip install -e ".[dev]"
pytest
```

## 라이선스

[Apache License 2.0](LICENSE). 자유롭게 사용·수정·재배포·상업적 이용이 가능하며,
변경 사항 고지와 라이선스·저작권 표기 유지 의무가 있습니다.
