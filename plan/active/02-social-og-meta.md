# 02. 소셜 공유 최적화 (정적 OG 메타태그)

> 우선순위: 🔴 높음 · 예상 규모: 0.5d · 위험: 낮음 · 사용자 액션: 도메인·문구 확인

## 배경 (검사 근거)

- `index.html`, `gunghap.html` 모두 `og:*`, `twitter:*`, `<meta name="description">`이 **0개**.
- 서비스의 핵심 행동이 "인스타/카톡/트위터 공유"인데, 링크를 붙여넣으면 **썸네일·제목·설명 없이 밋밋하게** 표시됨 → 클릭률·확산율 저하.
- 이 계획은 **모든 방문자에게 동일한 정적 미리보기**를 확보하는 단계. 결과별 맞춤 미리보기(예: "56점 무난한 궁합")는 03번(동적 OG)에서 다룸.

## 목표

두 페이지에 Open Graph / Twitter Card / description 메타태그와 대표 공유 이미지 1장을 추가해, 링크 공유 시 제대로 된 카드가 뜨게 한다.

## 작업 항목

- [x] 대표 OG 이미지(1200×630) 2장 제작 — `static/og/home-og.png`(4주 타일+제목), `static/og/gunghap-og.png`(십이간지 커플 캐릭터+제목). Playwright로 정적 렌더링해 커밋.
- [x] `templates/_meta.html` 공통 partial 생성 + `index.html`/`gunghap.html`에 include:
  - `og:title`, `og:description`, `og:image`(절대 URL), `og:url`, `og:type=website`, `og:locale=ko_KR`, `og:site_name`
  - `twitter:card=summary_large_image`, `twitter:title`, `twitter:description`, `twitter:image`
  - `<meta name="description">`, `<meta name="theme-color">`
  - `apple-mobile-web-app-capable`, `apple-mobile-web-app-title` (manifest.json은 범위 밖으로 보류)
- [x] 절대 URL 생성: `app.py`에 `PUBLIC_BASE_URL` 환경변수(기본값: 현재 Railway 프로덕션 주소) + `og_image_url()` 헬퍼를 `context_processor`로 전 템플릿에 주입
- [x] 파비콘 추가 — data URI SVG 이모지(홈 🀄, 궁합 💕)로 이미지 파일 없이 구현
- [x] 공유 텍스트 문구 확정 — 제안 문구 그대로 적용(아래 결과 참고)

## 내가(사용자) 할 일 — 답변 완료

1. **도메인**: 현재 Railway 주소(`lunar-ganzhi-calculator-production.up.railway.app`) 유지로 결정. `PUBLIC_BASE_URL` 환경변수로 되어 있어 나중에 커스텀 도메인으로 옮길 때 그 값만 바꾸면 됨(코드 수정 불필요).
2. **공유 카피**: 제안 문구 그대로 채택.
   - 홈: "사주 간지 계산기" / "생년월일시로 보는 나의 사주 · 대운 · 세운. 입춘·절기 기준 정통 명리 계산."
   - 궁합: "십이간지 커플 궁합 💕" / "생일로 보는 우리 궁합과 데이트 지역 추천"

## 검증 방법 (완료)

- 로컬에서 `curl`로 `/`, `/gunghap`의 `<head>` 메타태그 전수 출력 확인 — og/twitter/description/favicon 전부 정상, 절대 URL이 프로덕션 도메인으로 렌더됨.
- Playwright로 두 페이지 콘솔 에러 0건, 스크린샷으로 시각 회귀 없음 확인.
- 정적 이미지 `/static/og/*.png` 200 + `image/png` 응답 확인.
- ⏳ **배포 후 실제 검증은 미완료** (아래 참고)

## 리스크

- 낮음. 정적 태그 추가라 기능 영향 없음.
- 주의: 카카오톡은 OG를 강하게 캐싱 → 배포 후에도 옛 카드가 뜰 수 있음(카카오 디버거로 강제 갱신 필요, 배포 후 안내 예정).

## 리스크

- 낮음. 정적 태그 추가라 기능 영향 없음.
- 주의: 카카오톡은 OG를 강하게 캐싱 → 배포 후에도 옛 카드가 뜰 수 있음(디버거로 강제 갱신 안내 필요).
