# 02. 소셜 공유 최적화 (정적 OG 메타태그)

> 우선순위: 🔴 높음 · 예상 규모: 0.5d · 위험: 낮음 · 사용자 액션: 도메인·문구 확인

## 배경 (검사 근거)

- `index.html`, `gunghap.html` 모두 `og:*`, `twitter:*`, `<meta name="description">`이 **0개**.
- 서비스의 핵심 행동이 "인스타/카톡/트위터 공유"인데, 링크를 붙여넣으면 **썸네일·제목·설명 없이 밋밋하게** 표시됨 → 클릭률·확산율 저하.
- 이 계획은 **모든 방문자에게 동일한 정적 미리보기**를 확보하는 단계. 결과별 맞춤 미리보기(예: "56점 무난한 궁합")는 03번(동적 OG)에서 다룸.

## 목표

두 페이지에 Open Graph / Twitter Card / description 메타태그와 대표 공유 이미지 1장을 추가해, 링크 공유 시 제대로 된 카드가 뜨게 한다.

## 작업 항목

- [ ] 대표 OG 이미지(1200×630 권장) 1장 제작 — 십이간지 커플 캐릭터 + 서비스명. 기존 `zodiac.js` 캐릭터 재활용해 캔버스로 뽑거나 정적 PNG로 제작해 `static/og/` 에 저장
- [ ] `templates/index.html`, `templates/gunghap.html` `<head>`에 추가:
  - `og:title`, `og:description`, `og:image`(절대 URL), `og:url`, `og:type=website`, `og:locale=ko_KR`
  - `twitter:card=summary_large_image`, `twitter:title`, `twitter:image`
  - `<meta name="description">`, `<meta name="theme-color">`
  - 모바일 웹앱 느낌: `apple-mobile-web-app-*`, `manifest.json`(선택)
- [ ] 절대 URL 생성: 배포 도메인을 환경변수(`PUBLIC_BASE_URL`)로 두고 템플릿에서 조합 (하드코딩 금지 → 커스텀 도메인 이전 대비)
- [ ] 파비콘/터치아이콘 추가(하트 or 캐릭터)
- [ ] 공유 텍스트 문구 확정(제목/설명 카피)

## 내가(사용자) 할 일

1. **최종 도메인 결정**: 지금 `lunar-ganzhi-calculator-production.up.railway.app`을 계속 쓸지, 커스텀 도메인(예: `우리궁합.com`)을 붙일지. OG `og:url`·`og:image` 절대경로에 영향.
   - 커스텀 도메인 원하면: 도메인 구매 후 Railway 대시보드 → Settings → Domains에서 연결 (DNS CNAME 설정 필요).
2. **공유 카피 확인**: 예) 제목 "십이간지 커플 궁합 💕", 설명 "생일로 보는 우리 궁합과 데이트 지역 추천" — 이 문구로 갈지 검토/수정.
3. (선택) 대표 OG 이미지 시안 방향 피드백.

## 검증 방법

- 로컬에서 `<head>` 렌더 확인 + `curl`로 메타태그 출력 확인.
- 배포 후 실제 링크로 검증:
  - 카카오톡: 채팅방에 링크 붙여넣어 카드 확인 (카톡은 og 캐시가 강해 [카카오 디버거]로 갱신)
  - 페이스북/트위터: 공식 디버거(Sharing Debugger / Card Validator)로 미리보기 확인
- 모바일에서 "홈 화면에 추가" 시 아이콘·이름 확인.

## 리스크

- 낮음. 정적 태그 추가라 기능 영향 없음.
- 주의: 카카오톡은 OG를 강하게 캐싱 → 배포 후에도 옛 카드가 뜰 수 있음(디버거로 강제 갱신 안내 필요).
