/* ============================================================
   커플/친구 사주 궁합 데이트 — 화면 전환 + 렌더링 (바닐라 이식)
   원본: claude.ai/design "커플 사주 궁합 데이트.dc.html"
   - 5단계 플로우: landing → mode → input → reveal → result
   - 궁합 점수·등급은 검증된 백엔드(couple_compat/team_compat)를 그대로 쓴다.
   - 일간 관계(生/比/剋)·팀 라벨 문구는 디자인 콘텐츠라 여기 포팅한다.
   - 이 달의 동네 추천은 /gunghap/date-spots(월운 기반, 서버 계산)에서 가져온다.
   ============================================================ */

const EL_COLOR = { '목': '#5FB784', '화': '#DE6A54', '토': '#DCA94E', '금': '#C6CBD6', '수': '#6597CD' };
const EL_NAME = { '목': '목 · 나무', '화': '화 · 불', '토': '토 · 흙', '금': '금 · 쇠', '수': '수 · 물' };

const REVEAL_MSGS = ['사주를 세우는 중', '오행의 기운을 겹치는 중', '이번 달 월운을 읽는 중', '장소를 찾는 중'];
const FRIEND_TABLABEL = ['🙋 나', '👤 친구2', '👤 친구3', '👤 친구4'];
const FRIEND_STAMPLABEL = ['나', '친구2', '친구3', '친구4'];

const COUPLE_REL_COPY = {
    gen: { symbol: '生', label: '서로를 살려주는 상생(相生)의 인연', desc: '두 사람은 한쪽이 다른 쪽의 기운을 북돋아 주는 사이예요. 함께일수록 서로가 자라나고, 시간이 지날수록 편안해지는 궁합입니다.' },
    same: { symbol: '比', label: '같은 기운으로 통하는 비화(比和)의 인연', desc: '닮은 결을 가진 두 사람. 말하지 않아도 통하는 순간이 많지만, 가끔은 같은 고집이 부딪힐 수 있어요.' },
    ctrl: { symbol: '剋', label: '강하게 끌어당기는 상극(相剋)의 인연', desc: '불꽃 튀는 케미의 궁합. 서로 다른 기운이 팽팽히 당겨 설레지만, 균형을 잡으면 누구보다 단단해지는 사이예요.' },
};
const FRIEND_TEAM_COPY = {
    1: { label: '똑 닮은 한마음 팀', desc: '비슷한 기운을 가진 여러분. 취향도 리듬도 잘 맞아 어디를 가도 편안한 조합이에요.' },
    2: { label: '죽이 잘 맞는 콤비 팀', desc: '서로를 채워주는 기운이 만난 팀. 함께 다니면 확실히 시너지가 나요.' },
    3: { label: '균형 잡힌 삼합 팀', desc: '서로 다른 기운이 고르게 섞인 팀. 어떤 상황에서도 누군가는 중심을 잡아줘요.' },
    4: { label: '다채롭게 어우러지는 팀', desc: '오행이 골고루 모인 화려한 조합. 함께라면 못 할 게 없는 팀이에요.' },
};

const HOUR_OPTS = [
    { v: 'unknown', t: '시간을 잘 몰라요' },
    { v: '23-1', t: '23–01시 · 자시(子)' }, { v: '1-3', t: '01–03시 · 축시(丑)' },
    { v: '3-5', t: '03–05시 · 인시(寅)' }, { v: '5-7', t: '05–07시 · 묘시(卯)' },
    { v: '7-9', t: '07–09시 · 진시(辰)' }, { v: '9-11', t: '09–11시 · 사시(巳)' },
    { v: '11-13', t: '11–13시 · 오시(午)' }, { v: '13-15', t: '13–15시 · 미시(未)' },
    { v: '15-17', t: '15–17시 · 신시(申)' }, { v: '17-19', t: '17–19시 · 유시(酉)' },
    { v: '19-21', t: '19–21시 · 술시(戌)' }, { v: '21-23', t: '21–23시 · 해시(亥)' },
];

const PIN_POS = [{ top: '40%', left: '32%' }, { top: '58%', left: '60%' }, { top: '70%', left: '42%' }];

const DEFAULT_PEOPLE = [
    { y: 1996, m: 5, d: 20 }, { y: 1994, m: 11, d: 3 }, { y: 1997, m: 8, d: 15 }, { y: 1995, m: 2, d: 28 },
];

function defaultPerson(i) {
    const d = DEFAULT_PEOPLE[i] || { y: 1996, m: 1, d: 1 };
    return {
        year: d.y, month: d.m, day: d.d, hour: 'unknown', cal: 'solar',
        gender: i % 2 === 0 ? 'male' : 'female', name: '', leap: false,
    };
}

const state = {
    screen: 'landing',
    mode: 'couple',
    editIndex: 0,
    people: [],
    result: null,
    dateSpots: null,
    placesUnlocked: false,
    factorsOpen: false,
};
let revealTimer = null;

document.addEventListener('DOMContentLoaded', () => {
    populateSelects();
    bindStaticActions();
});

function opt(value, text) {
    const o = document.createElement('option');
    o.value = value;
    o.textContent = text;
    return o;
}

function populateSelects() {
    const yearSel = document.getElementById('f-year');
    for (let y = 2026; y >= 1940; y--) yearSel.appendChild(opt(y, `${y}년`));
    const monthSel = document.getElementById('f-month');
    for (let m = 1; m <= 12; m++) monthSel.appendChild(opt(m, `${m}월`));
    const daySel = document.getElementById('f-day');
    for (let d = 1; d <= 31; d++) daySel.appendChild(opt(d, `${d}일`));
    const hourSel = document.getElementById('f-hour');
    HOUR_OPTS.forEach((h) => hourSel.appendChild(opt(h.v, h.t)));
}

function bindStaticActions() {
    document.querySelectorAll('[data-action]').forEach((btn) => {
        btn.addEventListener('click', () => {
            const act = btn.dataset.action;
            if (act === 'start') showScreen('mode');
            else if (act === 'home') goHome();
            else if (act === 'back-mode') showScreen('mode');
            else if (act === 'calc') calc();
        });
    });
    document.querySelectorAll('[data-mode]').forEach((btn) => {
        btn.addEventListener('click', () => chooseMode(btn.dataset.mode));
    });
    document.querySelectorAll('.sj-caltabs .sj-tab').forEach((tab) => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.sj-caltabs .sj-tab').forEach((t) => t.classList.toggle('active', t === tab));
            updateCurrentPerson('cal', tab.dataset.cal);
            document.getElementById('f-leap-wrap').classList.toggle('show', tab.dataset.cal === 'lunar');
        });
    });
    document.getElementById('add-person-btn').addEventListener('click', addPerson);

    const form = document.getElementById('gunghap-form');
    form.addEventListener('change', (e) => {
        const t = e.target;
        if (t.name === 'gender') updateCurrentPerson('gender', t.value);
    });
    document.getElementById('f-name').addEventListener('input', (e) => updateCurrentPerson('name', e.target.value));
    document.getElementById('f-year').addEventListener('change', (e) => updateCurrentPerson('year', e.target.value));
    document.getElementById('f-month').addEventListener('change', (e) => updateCurrentPerson('month', e.target.value));
    document.getElementById('f-day').addEventListener('change', (e) => updateCurrentPerson('day', e.target.value));
    document.getElementById('f-hour').addEventListener('change', (e) => updateCurrentPerson('hour', e.target.value));
    document.getElementById('f-leap').addEventListener('change', (e) => updateCurrentPerson('leap', e.target.checked));
}

// ── 화면 전환 ─────────────────────────────
function showScreen(name) {
    state.screen = name;
    document.querySelectorAll('.sj-screen').forEach((s) => { s.hidden = s.dataset.screen !== name; });
    window.scrollTo(0, 0);
}

function goHome() {
    if (revealTimer) { clearTimeout(revealTimer); revealTimer = null; }
    state.result = null;
    state.dateSpots = null;
    state.placesUnlocked = false;
    state.factorsOpen = false;
    hideInputError();
    showScreen('landing');
}

function chooseMode(mode) {
    state.mode = mode;
    state.people = [defaultPerson(0), defaultPerson(1)];
    state.editIndex = 0;
    document.getElementById('input-title').textContent =
        mode === 'couple' ? '두 사람의 생일을 알려주세요' : '친구들의 생일을 알려주세요';
    document.getElementById('calc-btn').textContent =
        mode === 'couple' ? '💞 궁합 & 데이트 코스 보기' : '🧑‍🤝‍🧑 우리 케미 & 모임 장소 보기';
    hideInputError();
    renderPersonTabs();
    loadPersonIntoForm(0);
    showScreen('input');
}

// ── 다인 입력 (사람 탭 전환) ────────────────
function updateCurrentPerson(field, value) {
    state.people[state.editIndex][field] = value;
    renderPersonTabs(); // 요약 텍스트 갱신
}

function summaryOf(p) {
    const cal = p.cal === 'lunar' ? '음' : '양';
    return `${cal} ${String(p.year).slice(2)}.${p.month}.${p.day}`;
}

function renderPersonTabs() {
    const wrap = document.getElementById('person-tabs');
    const isCouple = state.mode === 'couple';
    wrap.innerHTML = state.people.map((p, i) => {
        const label = isCouple ? (i === 0 ? '🙋 나' : '💑 상대방') : FRIEND_TABLABEL[i];
        const removable = !isCouple && state.people.length > 2 && i > 0;
        return `
            <button type="button" class="sj-person-tab ${i === state.editIndex ? 'active' : ''}" data-tab-index="${i}">
                <div class="sj-person-tab-label">${label}</div>
                <div class="sj-person-tab-summary">${esc(summaryOf(p))}</div>
                ${removable ? `<span class="sj-person-tab-remove" data-remove-index="${i}">✕</span>` : ''}
            </button>`;
    }).join('');

    wrap.querySelectorAll('[data-tab-index]').forEach((btn) => {
        btn.addEventListener('click', (e) => {
            if (e.target.closest('[data-remove-index]')) return;
            loadPersonIntoForm(Number(btn.dataset.tabIndex));
        });
    });
    wrap.querySelectorAll('[data-remove-index]').forEach((btn) => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            removePerson(Number(btn.dataset.removeIndex));
        });
    });

    document.getElementById('add-person-btn').hidden = isCouple || state.people.length >= 4;
}

function loadPersonIntoForm(i) {
    state.editIndex = i;
    const p = state.people[i];
    document.getElementById('f-name').value = p.name;
    document.getElementById('f-year').value = String(p.year);
    document.getElementById('f-month').value = String(p.month);
    document.getElementById('f-day').value = String(p.day);
    document.getElementById('f-hour').value = p.hour;
    document.getElementById('f-leap').checked = !!p.leap;
    document.querySelector(`input[name="gender"][value="${p.gender}"]`).checked = true;
    document.querySelectorAll('.sj-caltabs .sj-tab').forEach((t) => t.classList.toggle('active', t.dataset.cal === p.cal));
    document.getElementById('f-leap-wrap').classList.toggle('show', p.cal === 'lunar');
    renderPersonTabs();
}

function addPerson() {
    if (state.people.length >= 4) return;
    state.people.push(defaultPerson(state.people.length));
    loadPersonIntoForm(state.people.length - 1);
}

function removePerson(i) {
    if (state.people.length <= 2) return;
    state.people.splice(i, 1);
    loadPersonIntoForm(Math.min(state.editIndex, state.people.length - 1));
}

// ── 계산 ──────────────────────────────────
function showInputError(msg) {
    const el = document.getElementById('input-error');
    el.textContent = msg;
    el.classList.add('show');
}
function hideInputError() {
    document.getElementById('input-error').classList.remove('show');
}

async function calc() {
    hideInputError();
    const fd = new FormData();
    fd.set('mode', state.mode);
    fd.set('count', String(state.people.length));
    state.people.forEach((p, i) => {
        const n = i + 1;
        fd.set(`p${n}_year`, p.year);
        fd.set(`p${n}_month`, p.month);
        fd.set(`p${n}_day`, p.day);
        fd.set(`p${n}_hour`, p.hour);
        fd.set(`p${n}_calendarType`, p.cal);
        fd.set(`p${n}_leapMonth`, p.leap ? 'true' : 'false');
        fd.set(`p${n}_gender`, p.gender);
        fd.set(`p${n}_name`, p.name);
    });

    showScreen('reveal');
    const msgDone = playRevealMessages();

    let data, spots;
    try {
        const [res, spotsRes] = await Promise.all([
            fetch('/gunghap/calculate', { method: 'POST', body: fd }),
            fetch('/gunghap/date-spots'),
        ]);
        data = await res.json();
        if (!res.ok) {
            cancelReveal();
            showInputError(data.error || '계산 중 오류가 발생했습니다.');
            showScreen('input');
            return;
        }
        spots = await spotsRes.json();
    } catch (err) {
        cancelReveal();
        showInputError('서버와 통신할 수 없습니다.');
        showScreen('input');
        return;
    }

    await msgDone;
    if (state.screen !== 'reveal') return;
    state.result = data;
    state.dateSpots = spots;
    state.placesUnlocked = false;
    state.factorsOpen = false;
    renderResult();
    showScreen('result');
}

function playRevealMessages() {
    const el = document.getElementById('reveal-msg');
    el.textContent = REVEAL_MSGS[0];
    return new Promise((resolve) => {
        let i = 0;
        const step = () => {
            i++;
            if (i < REVEAL_MSGS.length) {
                el.textContent = REVEAL_MSGS[i];
                revealTimer = setTimeout(step, 720);
            } else {
                revealTimer = null;
                resolve();
            }
        };
        revealTimer = setTimeout(step, 720);
    });
}
function cancelReveal() {
    if (revealTimer) { clearTimeout(revealTimer); revealTimer = null; }
}

// ── 결과: 대운 "현재" 컬럼 찾기 (전통나이 기준, 홈 화면과 동일 규칙) ──
function ageInYearsTraditional(birthDate, today) {
    let age = today.getFullYear() - birthDate.getFullYear();
    const hasHadBirthdayThisYear =
        today.getMonth() > birthDate.getMonth() ||
        (today.getMonth() === birthDate.getMonth() && today.getDate() >= birthDate.getDate());
    if (!hasHadBirthdayThisYear) age -= 1;
    return age;
}
function currentDaewoonPillar(daewoon, solar) {
    if (!daewoon || !daewoon.pillars || !daewoon.pillars.length) return null;
    const birthDate = new Date(solar.year, solar.month - 1, solar.day);
    const age = ageInYearsTraditional(birthDate, new Date());
    return daewoon.pillars.find((p) => age >= p.age && age < p.age + 10) || daewoon.pillars[0];
}

// ── 결과 렌더링 ───────────────────────────
function renderResult() {
    const r = state.result;
    const isCouple = r.compat.mode === 'couple';
    const persons = r.persons;

    const heroHtml = isCouple
        ? renderCoupleHero(persons, COUPLE_REL_COPY[r.compat.day_stem_relation].symbol)
        : renderFriendsHero(persons);
    const scoreHtml = isCouple ? renderCoupleScore(r) : renderFriendsScore(r);

    const now = new Date();
    const daeun = currentDaewoonPillar(persons[0].daewoon, persons[0].solar);
    const seun = r.luck_snapshot.seun;
    const wolun = r.luck_snapshot.wolun;
    const monthColor = EL_COLOR[wolun.branch_element];
    const monthGlow = monthColor + '44';

    const luckHtml = `
        <div class="sj-pillars-title">지금 우리에게 흐르는 기운</div>
        <div class="sj-pillars-hint">이번 달 장소는 <b style="color:#C9B27A;">월운</b>이 이끌어요</div>
        <div class="sj-luck3-grid">
            <div class="sj-luck3-card">
                <div class="sj-luck3-label">대운 · 큰 흐름</div>
                <div class="sj-luck3-hanja" style="color:${daeun ? EL_COLOR[daeun.branch_element] : '#77704F'};">${daeun ? esc(daeun.hanja) : '—'}</div>
                <div class="sj-luck3-name">${daeun ? esc(EL_NAME[daeun.branch_element]) : '시간 모름'}</div>
            </div>
            <div class="sj-luck3-card">
                <div class="sj-luck3-label">세운 · ${now.getFullYear()}</div>
                <div class="sj-luck3-hanja" style="color:${EL_COLOR[seun.branch_element]};">${esc(seun.hanja)}</div>
                <div class="sj-luck3-name">${esc(EL_NAME[seun.branch_element])}</div>
            </div>
            <div class="sj-luck3-card month" style="--month-color:${monthColor}; --month-glow:${monthGlow};">
                <div class="sj-luck3-badge">이번 달</div>
                <div class="sj-luck3-label">월운 · ${now.getMonth() + 1}월</div>
                <div class="sj-luck3-hanja" style="color:${monthColor};">${esc(wolun.hanja)}</div>
                <div class="sj-luck3-name">${esc(EL_NAME[wolun.branch_element])}</div>
            </div>
        </div>
    `;

    const nbhHtml = renderNeighborhood(monthColor, monthGlow, isCouple);

    const html = `
        <div class="sj-origin">${isCouple ? '우리 두 사람의 궁합' : '우리 팀의 케미 궁합'}</div>
        ${heroHtml}
        ${scoreHtml}
        <div class="sj-divider"></div>
        ${luckHtml}
        ${nbhHtml}
        <div class="sj-share">
            <button type="button" class="sj-btn-gold" data-share-card>🎴 우리 궁합 카드 공유하기</button>
            <button type="button" class="sj-btn-ghost" data-plan>📅 이 코스로 일정 만들기</button>
            <button type="button" class="sj-btn-text" data-action="home">처음부터 다시 보기</button>
        </div>
        <div class="sj-toast" id="share-toast"></div>
    `;

    const el = document.getElementById('result');
    el.innerHTML = html;
    bindResultActions(el);
}

function renderCoupleHero(persons, relSymbol) {
    const [a, b] = persons;
    const aEl = a.day_element, bEl = b.day_element;
    return `
        <div class="sj-couple-hero">
            <div class="sj-couple-row">
                <div class="sj-couple-person">
                    <div class="sj-couple-stamp" style="border-color:${EL_COLOR[aEl]}; color:${EL_COLOR[aEl]}; text-shadow:0 0 20px ${EL_COLOR[aEl]}66;">${esc(a.day_pillar_hanja[0])}</div>
                    <div class="sj-couple-person-label">나 · ${esc(a.day_pillar[0])}(${esc(elHanja(aEl))})</div>
                </div>
                <div class="sj-couple-rel-symbol">${esc(relSymbol)}</div>
                <div class="sj-couple-person">
                    <div class="sj-couple-stamp" style="border-color:${EL_COLOR[bEl]}; color:${EL_COLOR[bEl]}; text-shadow:0 0 20px ${EL_COLOR[bEl]}66;">${esc(b.day_pillar_hanja[0])}</div>
                    <div class="sj-couple-person-label">상대 · ${esc(b.day_pillar[0])}(${esc(elHanja(bEl))})</div>
                </div>
            </div>
        </div>`;
}

function renderFriendsHero(persons) {
    const stamps = persons.map((p, i) => `
        <div class="sj-friend-stamp-wrap">
            <div class="sj-friend-stamp" style="border-color:${EL_COLOR[p.day_element]}; color:${EL_COLOR[p.day_element]}; text-shadow:0 0 16px ${EL_COLOR[p.day_element]}66;">${esc(p.day_pillar_hanja[0])}</div>
            <div class="sj-person-tab-label" style="font-size:11px;color:#B8AE8C;">${esc(p.name || FRIEND_STAMPLABEL[i])} · ${esc(p.day_pillar[0])}(${esc(elHanja(p.day_element))})</div>
        </div>`).join('');
    return `<div class="sj-friends-hero"><div class="sj-friends-row">${stamps}</div></div>`;
}

function elHanja(el) {
    return { '목': '木', '화': '火', '토': '土', '금': '金', '수': '水' }[el] || el;
}

function renderCoupleScore(r) {
    const rel = COUPLE_REL_COPY[r.compat.day_stem_relation];
    const factorsHtml = renderFactorsToggle(r.compat.factors);
    return `
        <div style="text-align:center;">
            <div class="sj-score-big">${r.compat.score}<span>점</span></div>
            <div class="sj-score-badge">${esc(r.compat.grade)}</div>
            <div class="sj-daystem-rel">${esc(rel.label)}</div>
            <p class="sj-compat-desc">${esc(rel.desc)}</p>
            ${factorsHtml}
        </div>`;
}

function renderFriendsScore(r) {
    const team = FRIEND_TEAM_COPY[Math.min(r.compat.unique_day_elements, 4)];
    const factorsHtml = renderPairwiseToggle(r.compat.pairwise, r.persons);
    return `
        <div style="text-align:center;">
            <div class="sj-score-big">${r.compat.score}<span>점</span></div>
            <div class="sj-score-badge">${esc(r.compat.grade)}</div>
            <div class="sj-daystem-rel">${esc(team.label)}</div>
            <p class="sj-compat-desc">${esc(team.desc)}</p>
            ${factorsHtml}
        </div>`;
}

function renderFactorsToggle(factors) {
    if (!factors || !factors.length) return '';
    const list = factors.map((f) => `
        <div class="sj-relation-card">
            <span class="sj-relation-kind">${f.delta >= 0 ? '+' : ''}${f.delta}</span>
            <span>${esc(f.label)} — ${esc(f.desc)}</span>
        </div>`).join('');
    return `
        <button type="button" class="sj-factors-toggle" data-toggle-factors>궁합 풀이 자세히 보기</button>
        <div class="sj-factors-list" id="factors-list" hidden>${list}</div>`;
}

function renderPairwiseToggle(pairwise, persons) {
    if (!pairwise || !pairwise.length) return '';
    const nameOf = (i) => persons[i].name || FRIEND_STAMPLABEL[i];
    const list = pairwise.map((p) => `
        <div class="sj-relation-card">
            <span class="sj-relation-kind">${p.score}</span>
            <span>${esc(nameOf(p.a))} · ${esc(nameOf(p.b))} — ${esc(p.grade)}</span>
        </div>`).join('');
    return `
        <button type="button" class="sj-factors-toggle" data-toggle-factors>짝별 궁합 자세히 보기</button>
        <div class="sj-factors-list" id="factors-list" hidden>${list}</div>`;
}

function renderNeighborhood(monthColor, monthGlow, isCouple) {
    const spots = state.dateSpots;
    if (!spots) return '';
    const nbh = spots.neighborhood;
    const rawPlaces = spots.sample ? spots.places : [...(spots.cafe || []), ...(spots.food || [])];
    const places = rawPlaces.slice(0, 3);

    const pins = places.map((p, i) => {
        const locked = i > 0 && !state.placesUnlocked;
        return `
            <div class="sj-map-pin" style="top:${PIN_POS[i].top};left:${PIN_POS[i].left};">
                <div class="sj-map-pin-diamond" style="background:${locked ? '#4a4535' : 'linear-gradient(135deg,#F0E0AE,#D4B36A)'}; opacity:${locked ? .55 : 1};">
                    <span>${locked ? '🔒' : i + 1}</span>
                </div>
            </div>`;
    }).join('');

    const firstCard = places[0] ? placeCard(places[0], 1) : '';
    let restHtml;
    if (places.length <= 1) {
        restHtml = '';
    } else if (state.placesUnlocked) {
        restHtml = places.slice(1).map((p, i) => placeCard(p, i + 2)).join('');
    } else {
        restHtml = lockedTeaser(places.length - 1);
    }

    return `
        <div class="sj-nbh-card">
            <div class="sj-nbh-body">
                <div class="sj-nbh-kicker">${isCouple ? '이 달의 데이트 동네' : '이 달의 모임 동네'}</div>
                <div class="sj-nbh-title-row">
                    <div class="sj-nbh-name">${esc(nbh.name)}</div>
                    <div class="sj-nbh-tag" style="color:${monthColor};">${esc(nbh.tag)}</div>
                </div>
                <p class="sj-nbh-why">${esc(nbh.why)}</p>
            </div>
            <div class="sj-mock-map">
                <div class="land1"></div><div class="land2"></div>
                <div class="glowspot" style="background:radial-gradient(circle, ${monthGlow} 0%, transparent 70%);"></div>
                ${pins}
                <div class="sj-map-badge">
                    <div class="sj-map-badge-inner">
                        <span class="sj-map-badge-k">K</span>
                        <span class="sj-map-badge-text">${esc(nbh.name)} ${isCouple ? '데이트 코스' : '모임 코스'}</span>
                    </div>
                </div>
                <div class="sj-map-credit">kakao map</div>
            </div>
            ${spots.sample ? `<div class="sj-sample-notice">ℹ️ ${esc(spots.notice)}</div>` : ''}
        </div>
        <div class="sj-places-wrap">${firstCard}${restHtml}</div>
    `;
}

function placeCard(p, num) {
    return `
        <div class="sj-place-card">
            <div class="sj-place-diamond"><span>${num}</span></div>
            <div class="sj-place-body">
                <div class="sj-place-name-row">
                    <span class="sj-place-name">${esc(p.name)}</span>
                    <span class="sj-place-cat">${esc(p.category)}</span>
                </div>
                <div class="sj-place-blurb">${esc(p.address || '')}</div>
            </div>
            ${p.url ? `<a class="sj-place-btn" href="${esc(p.url)}" target="_blank" rel="noopener">길찾기</a>` : ''}
        </div>`;
}

function lockedTeaser(count) {
    return `
        <div class="sj-place-locked">
            <div class="sj-place-locked-skeleton">
                <div class="sj-place-locked-row"><div class="sj-place-locked-diamond"></div>
                    <div style="flex:1;"><div class="sj-place-locked-bar1"></div><div class="sj-place-locked-bar2"></div></div></div>
                <div class="sj-place-locked-row"><div class="sj-place-locked-diamond"></div>
                    <div style="flex:1;"><div class="sj-place-locked-bar1" style="width:48%;"></div><div class="sj-place-locked-bar2" style="width:68%;"></div></div></div>
            </div>
            <div class="sj-place-locked-overlay">
                <div class="ic">🔒</div>
                <div class="t1">숨은 맛집·카페 ${count}곳 더 있어요</div>
                <div class="t2">인스타·카톡에 공유하면 바로 열려요</div>
                <button type="button" class="sj-unlock" data-unlock-places>📲 공유하고 ${count}곳 더 열기</button>
            </div>
        </div>`;
}

function bindResultActions(el) {
    el.querySelector('[data-unlock-places]')?.addEventListener('click', () => {
        state.placesUnlocked = true;
        renderResult();
    });
    el.querySelector('[data-toggle-factors]')?.addEventListener('click', () => {
        state.factorsOpen = !state.factorsOpen;
        const list = document.getElementById('factors-list');
        if (list) list.hidden = !state.factorsOpen;
    });
    el.querySelector('[data-share-card]')?.addEventListener('click', () => {
        toast('궁합 카드 이미지 저장은 곧 제공될 예정이에요.');
    });
    el.querySelector('[data-plan]')?.addEventListener('click', () => {
        toast('일정 만들기 기능은 곧 제공될 예정이에요.');
    });
    el.querySelector('[data-action="home"]')?.addEventListener('click', goHome);
}

let toastTimer = null;
function toast(msg) {
    const el = document.getElementById('share-toast');
    if (!el) return;
    el.textContent = msg;
    el.style.opacity = '1';
    if (toastTimer) clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { el.style.opacity = '0'; }, 2600);
}

function esc(str) {
    const div = document.createElement('div');
    div.textContent = str == null ? '' : String(str);
    return div.innerHTML;
}
