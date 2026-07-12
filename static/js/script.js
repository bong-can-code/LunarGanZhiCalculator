/* ============================================================
   사주 간지 계산기 — 화면 전환 + 렌더링 (바닐라 이식)
   원본: claude.ai/design "사주 간지 계산기.dc.html"
   - 4단계 플로우: landing → input → reveal → result
   - 간이 클라이언트 계산 대신 정확한 /calculate 백엔드에 연결한다.
   - 일주 이름/키워드/설명은 디자인 콘텐츠라 여기 포팅한다.
   ============================================================ */

// ── 디자인 데이터: 천간 10 (일주 해설용) ──────────────────
const STEMS = {
    '갑': { el: '목', name: '하늘로 뻗는 큰 나무', kw: ['리더십', '뚝심', '정직'], desc: '하늘을 향해 곧게 자라는 아름드리 나무. 한번 세운 뜻은 좀처럼 꺾이지 않고, 사람들은 어느새 당신을 기둥처럼 기대고 있어요.' },
    '을': { el: '목', name: '바람에 휘는 화초·덩굴', kw: ['유연함', '생명력', '섬세'], desc: '바위 틈에서도 기어이 꽃을 피우는 덩굴. 부드럽지만 끈질기고, 어떤 환경에 놓여도 살아남는 생존의 지혜를 지녔어요.' },
    '병': { el: '화', name: '온 세상을 비추는 태양', kw: ['열정', '밝음', '솔직'], desc: '한낮의 태양처럼 숨길 수 없는 열정으로 주변을 데우는 사람. 그 빛은 사람을 끌어모으지만, 때론 스스로 너무 뜨겁기도 해요.' },
    '정': { el: '화', name: '어둠을 밝히는 촛불', kw: ['따뜻함', '헌신', '통찰'], desc: '어둠 속을 은은히 밝히는 촛불. 곁에 있는 사람의 마음을 세심히 읽어내고, 필요한 순간 조용히 온기를 건네요.' },
    '무': { el: '토', name: '묵직하게 선 큰 산', kw: ['신뢰', '포용', '중심'], desc: '쉽게 흔들리지 않는 큰 산 같은 사람. 많은 이들이 당신의 품에서 안정을 찾고, 당신은 그 무게를 기꺼이 견뎌내요.' },
    '기': { el: '토', name: '만물을 기르는 기름진 땅', kw: ['포용', '실속', '현실감'], desc: '조용히 만물을 길러내는 논밭. 티 내지 않고 사람과 재물을 모으며, 넓은 품으로 곁을 채워주는 현실적인 지혜가 있어요.' },
    '경': { el: '금', name: '제련 전의 무쇠·원석', kw: ['의리', '결단', '강단'], desc: '아직 다듬어지지 않은 무쇠와 원석. 강단 있고 의리가 깊으며, 옳다고 믿는 일 앞에서는 결코 물러서지 않아요.' },
    '신': { el: '금', name: '세공된 보석·서릿발', kw: ['예민', '안목', '자존심'], desc: '정교하게 세공된 보석처럼 빛나는 사람. 남다른 감각과 자존심을 지녔고, 아름다움과 완성도를 알아보는 눈이 특별해요.' },
    '임': { el: '수', name: '모든 것을 품는 바다', kw: ['깊이', '자유', '포용'], desc: '모든 물줄기를 받아들이는 넓은 바다. 생각이 깊고 자유로우며, 그 속은 쉽게 들키지 않아 늘 여운을 남겨요.' },
    '계': { el: '수', name: '새벽에 맺히는 이슬', kw: ['총명', '섬세', '스며듦'], desc: '새벽에 맺히는 맑은 이슬과 시냇물. 총명하고 섬세하며, 스며들듯 사람의 마음을 적시는 조용한 힘이 있어요.' },
};

// 지지 → 띠 이모지·동물 (지지 한글 기준)
const BRANCH_ANIMAL = {
    '자': '🐭 쥐', '축': '🐮 소', '인': '🐯 호랑이', '묘': '🐰 토끼',
    '진': '🐲 용', '사': '🐍 뱀', '오': '🐴 말', '미': '🐑 양',
    '신': '🐵 원숭이', '유': '🐔 닭', '술': '🐶 개', '해': '🐷 돼지',
};

// 오행 색상
const EL_COLOR = { '목': '#5FB784', '화': '#DE6A54', '토': '#DCA94E', '금': '#C6CBD6', '수': '#6597CD' };

const STEM_ORDER = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계'];
const BRANCH_ORDER = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해'];

const REVEAL_MSGS = ['별을 읽고 있어요', '천간을 세우는 중', '지지를 맞추는 중', '네 기둥이 완성됐어요'];
const TODAY_LINES = [
    '흐름을 거스르지 말고 한 박자 쉬어가면 뜻밖의 기회가 열리는 날이에요.',
    '오늘은 당신의 말 한마디가 사람을 움직여요. 먼저 손 내밀어 보세요.',
    '작은 지출을 조심하되, 마음이 끌리는 만남은 놓치지 마세요.',
    '미뤄둔 일을 매듭짓기 좋은 날. 집중력이 유난히 선명해요.',
    '감정보다 실리를 택하면 하루가 한결 가벼워집니다.',
];
const HOUR_OPTS = [
    { v: 'unknown', t: '시간을 잘 몰라요' },
    { v: '23-1', t: '23–01시 · 자시(子)' }, { v: '1-3', t: '01–03시 · 축시(丑)' },
    { v: '3-5', t: '03–05시 · 인시(寅)' }, { v: '5-7', t: '05–07시 · 묘시(卯)' },
    { v: '7-9', t: '07–09시 · 진시(辰)' }, { v: '9-11', t: '09–11시 · 사시(巳)' },
    { v: '11-13', t: '11–13시 · 오시(午)' }, { v: '13-15', t: '13–15시 · 미시(未)' },
    { v: '15-17', t: '15–17시 · 신시(申)' }, { v: '17-19', t: '17–19시 · 유시(酉)' },
    { v: '19-21', t: '19–21시 · 술시(戌)' }, { v: '21-23', t: '21–23시 · 해시(亥)' },
];

const PILLAR_KEYS = ['hour', 'day', 'month', 'year'];
const PILLAR_SHORT = { hour: '시주', day: '일주', month: '월주', year: '년주' };
const GIL_SET = new Set(['천을귀인', '천덕귀인', '월덕귀인', '문곡귀인', '학당귀인', '암록']);

// ── 상태 ──────────────────────────────────
const state = {
    screen: 'landing',
    cal: 'solar',
    result: null,
    allRevealed: false,
    locked: true,
    manseTab: 'wongook',
    relSubtab: 'ganji',
};
let revealTimer = null;

// ── 초기화 ────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    populateSelects();
    bindActions();
});

function populateSelects() {
    const yearSel = document.getElementById('f-year');
    for (let y = 2026; y >= 1940; y--) yearSel.appendChild(opt(y, `${y}년`));
    yearSel.value = '1996';

    const monthSel = document.getElementById('f-month');
    for (let m = 1; m <= 12; m++) monthSel.appendChild(opt(m, `${m}월`));
    monthSel.value = '5';

    const daySel = document.getElementById('f-day');
    for (let d = 1; d <= 31; d++) daySel.appendChild(opt(d, `${d}일`));
    daySel.value = '20';

    const hourSel = document.getElementById('f-hour');
    HOUR_OPTS.forEach((h) => hourSel.appendChild(opt(h.v, h.t)));
    hourSel.value = 'unknown';
}

function opt(value, text) {
    const o = document.createElement('option');
    o.value = value;
    o.textContent = text;
    return o;
}

function bindActions() {
    // data-action 버튼 (start / home / calc)
    document.querySelectorAll('[data-action]').forEach((btn) => {
        btn.addEventListener('click', () => {
            const act = btn.dataset.action;
            if (act === 'start') showScreen('input');
            else if (act === 'home') goHome();
            else if (act === 'calc') calc();
        });
    });

    // 양력/음력 탭
    document.querySelectorAll('.sj-tab').forEach((tab) => {
        tab.addEventListener('click', () => {
            state.cal = tab.dataset.cal;
            document.querySelectorAll('.sj-tab').forEach((t) => t.classList.toggle('active', t === tab));
            document.getElementById('f-leap-wrap').classList.toggle('show', state.cal === 'lunar');
            hideInputError();
        });
    });
}

// ── 화면 전환 ─────────────────────────────
function showScreen(name) {
    state.screen = name;
    document.querySelectorAll('.sj-screen').forEach((s) => {
        s.hidden = s.dataset.screen !== name;
    });
    window.scrollTo(0, 0);
}

function goHome() {
    if (revealTimer) { clearTimeout(revealTimer); revealTimer = null; }
    state.result = null;
    state.allRevealed = false;
    state.locked = true;
    state.manseTab = 'wongook';
    state.relSubtab = 'ganji';
    hideInputError();
    showScreen('landing');
}

// ── 입력 → 계산 ───────────────────────────
async function calc() {
    hideInputError();
    const fd = new FormData();
    fd.set('year', document.getElementById('f-year').value);
    fd.set('month', document.getElementById('f-month').value);
    fd.set('day', document.getElementById('f-day').value);
    fd.set('hour', document.getElementById('f-hour').value);
    fd.set('calendarType', state.cal);
    fd.set('leapMonth', document.getElementById('f-leap').checked ? 'true' : 'false');
    // 디자인에 성별 입력이 없다. 성별은 대운(순행/역행)에만 쓰이고 이 화면에는
    // 대운을 표시하지 않으므로, 4주·오행 계산에 영향 없는 기본값을 보낸다.
    fd.set('gender', 'male');

    showScreen('reveal');
    const msgDone = playRevealMessages();

    let data;
    try {
        const res = await fetch('/calculate', { method: 'POST', body: fd });
        data = await res.json();
        if (!res.ok) {
            cancelReveal();
            showInputError(data.error || '계산 중 오류가 발생했습니다.');
            showScreen('input');
            return;
        }
    } catch (err) {
        cancelReveal();
        showInputError('서버와 통신할 수 없습니다.');
        showScreen('input');
        return;
    }

    await msgDone;
    if (state.screen !== 'reveal') return; // 도중에 홈으로 이탈한 경우
    state.result = data;
    state.allRevealed = false;
    state.locked = true;
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

function showInputError(msg) {
    const el = document.getElementById('input-error');
    el.textContent = msg;
    el.classList.add('show');
}
function hideInputError() {
    document.getElementById('input-error').classList.remove('show');
}

// ── 결과 렌더링 ───────────────────────────
function gapjaIndex(stem, branch) {
    const s = STEM_ORDER.indexOf(stem);
    const b = BRANCH_ORDER.indexOf(branch);
    for (let i = 0; i < 60; i++) {
        if (i % 10 === s && i % 12 === b) return i;
    }
    return 0;
}

// 오늘 날짜의 일간지 순번 (오늘의 운세 점수용, 흐름 연출값)
function dayIndexAnchor(y, m, d) {
    const anchor = Date.UTC(1984, 1, 2); // 갑자일 기준
    const diff = Math.round((Date.UTC(y, m - 1, d) - anchor) / 86400000);
    return ((diff % 60) + 60) % 60;
}

function pillarCard(label, p, covered) {
    if (!p) {
        return `
            <div class="sj-pillar">
                <div class="sj-pillar-label">${label}</div>
                <div class="sj-pillar-stem" style="color:#8A815F;">—</div>
                <div class="sj-pillar-branch" style="color:#8A815F;"></div>
                <div class="sj-pillar-kr">시간 모름</div>
                <div class="sj-pillar-animal"></div>
            </div>`;
    }
    const cover = covered
        ? `<div class="sj-pillar-cover"><span>?</span></div>`
        : '';
    return `
        <div class="sj-pillar">
            <div class="sj-pillar-label">${label}</div>
            <div class="sj-pillar-stem" style="color:${EL_COLOR[p.stem_element]};">${esc(p.hanja[0])}</div>
            <div class="sj-pillar-branch" style="color:${EL_COLOR[p.branch_element]};">${esc(p.hanja[1])}</div>
            <div class="sj-pillar-kr">${esc(p.korean)}</div>
            <div class="sj-pillar-animal">${BRANCH_ANIMAL[p.branch] || ''}</div>
            ${cover}
        </div>`;
}

// ── 만세력 탭: 사주원국 ────────────────────
function wongookCell(p, field) {
    if (!p) return '-';
    if (field === 'hidden_stems') return p.hidden_stems.join(' ');
    if (field === 'gongmang') return p.is_gongmang ? p.branch : '-';
    return p[field] != null ? p[field] : '-';
}

function renderWongookTab(r) {
    const rows = [
        { label: '십성', field: 'sipseong_stem', tooltip: 'sipseong' },
        { label: '천간', field: '__stem_tile' },
        { label: '지지', field: '__branch_tile' },
        { label: '십성', field: 'sipseong_branch', tooltip: 'sipseong' },
        { label: '지장간', field: 'hidden_stems', tooltip: 'jijanggan' },
        { label: '12운성', field: 'unseong12', tooltip: 'unseong12' },
        { label: '12신살', field: 'sinsal12', tooltip: 'sinsal12' },
        { label: '공망', field: 'gongmang', tooltip: 'gongmang' },
    ];

    let html = `
        <div class="sj-manse-title" style="display:flex;align-items:center;gap:6px;">
            사주원국 <button type="button" class="sj-help-btn" data-tooltip="wongook">?</button>
        </div>
        <div class="sj-wongook-grid"><div></div>`;
    PILLAR_KEYS.forEach((k) => { html += `<div class="head">${PILLAR_SHORT[k]}</div>`; });

    rows.forEach((row) => {
        const labelCls = row.tooltip ? 'rowlabel sj-rowlabel-tap' : 'rowlabel';
        const labelAttr = row.tooltip ? ` data-tooltip="${row.tooltip}"` : '';
        html += `<div class="${labelCls}"${labelAttr}>${row.label}</div>`;
        PILLAR_KEYS.forEach((k) => {
            const p = r.pillars[k];
            if (row.field === '__stem_tile') {
                html += p
                    ? `<div class="stem-tile" style="color:${EL_COLOR[p.stem_element]};">${esc(p.hanja[0])}<span>${esc(p.yin_yang_stem)}</span></div>`
                    : `<div class="stem-tile" style="color:#77704F;">-</div>`;
            } else if (row.field === '__branch_tile') {
                html += p
                    ? `<div class="branch-tile" style="color:${EL_COLOR[p.branch_element]};">${esc(p.hanja[1])}<span>${esc(p.yin_yang_branch)}</span></div>`
                    : `<div class="branch-tile" style="color:#77704F;">-</div>`;
            } else {
                html += `<div>${esc(wongookCell(p, row.field))}</div>`;
            }
        });
    });
    html += '</div>';
    return html;
}

// ── 만세력 탭: 사주관계 (천간과 지지 / 신살과 길성) ─────────
function relationCard(rel) {
    return `<div class="sj-relation-card"><span class="sj-relation-kind">${esc(rel.kind)}</span><span>${esc(rel.pillars.join('·'))} — ${esc(rel.note)}</span></div>`;
}

function renderRelationsGanji(r) {
    const stemsHtml = r.relations.stems.length
        ? r.relations.stems.map(relationCard).join('')
        : '<div class="sj-empty-state">천간끼리는 특별한 합·충이 없어요</div>';
    const branchesHtml = r.relations.branches.length
        ? r.relations.branches.map(relationCard).join('')
        : '<div class="sj-empty-state">지지끼리는 특별한 합·충이 없어요</div>';
    return `
        <div class="sj-manse-title">천간 관계</div>
        ${stemsHtml}
        <div class="sj-manse-title" style="margin-top:18px;">지지 관계</div>
        ${branchesHtml}
    `;
}

function gilseongTagList(tags) {
    if (!tags || !tags.length) return `<div class="sj-gilseong-tags"><span class="sj-gilseong-tag sal">-</span></div>`;
    return `<div class="sj-gilseong-tags">${tags.map((t) => `<span class="sj-gilseong-tag ${GIL_SET.has(t) ? 'gil' : 'sal'}">${esc(t)}</span>`).join('')}</div>`;
}

function renderRelationsSinsal(r) {
    let html = '<div class="sj-wongook-grid"><div></div>';
    PILLAR_KEYS.forEach((k) => { html += `<div class="head">${PILLAR_SHORT[k]}</div>`; });
    html += '<div class="rowlabel">천간</div>';
    PILLAR_KEYS.forEach((k) => {
        const p = r.pillars[k];
        html += p
            ? `<div class="stem-tile" style="color:${EL_COLOR[p.stem_element]};font-size:16px;">${esc(p.hanja[0])}</div>`
            : '<div>-</div>';
    });
    html += '<div class="rowlabel">길성</div>';
    PILLAR_KEYS.forEach((k) => { html += `<div>${gilseongTagList(r.gilseong.stems[k])}</div>`; });
    html += '</div>';

    html += '<div class="sj-wongook-grid" style="margin-top:14px;"><div></div>';
    PILLAR_KEYS.forEach((k) => { html += `<div class="head">${PILLAR_SHORT[k]}</div>`; });
    html += '<div class="rowlabel">지지</div>';
    PILLAR_KEYS.forEach((k) => {
        const p = r.pillars[k];
        html += p
            ? `<div class="branch-tile" style="color:${EL_COLOR[p.branch_element]};font-size:16px;">${esc(p.hanja[1])}</div>`
            : '<div>-</div>';
    });
    html += '<div class="rowlabel">길성</div>';
    PILLAR_KEYS.forEach((k) => { html += `<div>${gilseongTagList(r.gilseong.branches[k])}</div>`; });
    html += '</div>';
    return html;
}

function renderRelationsTab(r) {
    const sub = state.relSubtab;
    return `
        <div class="sj-subtabs">
            <button type="button" class="sj-subtab ${sub === 'ganji' ? 'active' : ''}" data-relsub="ganji">천간과 지지</button>
            <button type="button" class="sj-subtab ${sub === 'sinsal' ? 'active' : ''}" data-relsub="sinsal">신살과 길성</button>
        </div>
        ${sub === 'sinsal' ? renderRelationsSinsal(r) : renderRelationsGanji(r)}
    `;
}

// ── 만세력 탭: 오행과 십성 ─────────────────
function pentPoint(k, r, cx, cy) {
    const angle = ((-90 + k * 72) * Math.PI) / 180;
    return [cx + r * Math.cos(angle), cy + r * Math.sin(angle)];
}

function renderOhaengPentagon(pct) {
    const order = ['목', '화', '토', '금', '수'];
    const cx = 140, cy = 140, radius = 88, nodeR = 30;
    const pts = order.map((_, k) => pentPoint(k, radius, cx, cy));

    let edges = '';
    for (let i = 0; i < 5; i++) {
        const [x1, y1] = pts[i];
        const [x2, y2] = pts[(i + 1) % 5];
        edges += `<line x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}" stroke="rgba(212,179,106,.4)" stroke-width="1.5" marker-end="url(#sj-arrow)" />`;
    }
    let stars = '';
    for (let i = 0; i < 5; i++) {
        const [x1, y1] = pts[i];
        const [x2, y2] = pts[(i + 2) % 5];
        stars += `<line x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}" stroke="rgba(255,255,255,.14)" stroke-width="1" stroke-dasharray="3,4" />`;
    }
    let nodes = '';
    order.forEach((el, k) => {
        const [x, y] = pts[k];
        const value = pct[el] || 0;
        const dim = value === 0;
        nodes += `
            <g>
                <circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${nodeR}" fill="${dim ? 'rgba(255,255,255,.03)' : 'rgba(212,179,106,.1)'}" stroke="${dim ? 'rgba(255,255,255,.12)' : EL_COLOR[el]}" stroke-width="1.5" />
                <text x="${x.toFixed(1)}" y="${(y - 4).toFixed(1)}" text-anchor="middle" font-family="'Noto Serif KR', serif" font-size="16" font-weight="700" fill="${dim ? '#77704F' : EL_COLOR[el]}">${el}</text>
                <text x="${x.toFixed(1)}" y="${(y + 14).toFixed(1)}" text-anchor="middle" font-family="'Noto Sans KR', sans-serif" font-size="11" fill="${dim ? '#77704F' : '#EDE4CC'}">${value}%</text>
            </g>`;
    });

    return `
        <svg viewBox="0 0 280 280" width="240" height="240" role="img" aria-label="오행 분포 오각형 다이어그램">
            <defs>
                <marker id="sj-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                    <path d="M0,0 L10,5 L0,10 z" fill="rgba(212,179,106,.55)" />
                </marker>
            </defs>
            ${stars}
            ${edges}
            ${nodes}
        </svg>`;
}

function renderOhaengTab(r) {
    const a = r.analysis;
    const GROUP_ORDER = [
        ['비겁', ['비견', '겁재']], ['식상', ['식신', '상관']], ['재성', ['편재', '정재']],
        ['관성', ['편관', '정관']], ['인성', ['편인', '정인']],
    ];

    const cards = GROUP_ORDER.map(([group, names]) => {
        const el = a.groups[group].element;
        const groupPct = a.groups[group].pct;
        const st = a.element_status[el];
        const detail = names.map((n) => `${n} ${a.sipseong_pct[n]}%`).join(' · ');
        return `
            <div class="sj-ohaeng-card">
                <div class="sj-ohaeng-swatch" style="background:${EL_COLOR[el]}22;color:${EL_COLOR[el]};">${el}</div>
                <div class="sj-ohaeng-body">
                    <div class="sj-ohaeng-name">${el}(${group}) <span class="sj-badge ${st}">${st}</span></div>
                    <div class="sj-ohaeng-detail">${detail}</div>
                </div>
                <div class="sj-ohaeng-pct" style="color:${EL_COLOR[el]};">${groupPct}%</div>
            </div>`;
    }).join('');

    return `
        <div class="sj-manse-title" style="display:flex;align-items:center;gap:6px;">
            오행과 십성 <button type="button" class="sj-help-btn" data-tooltip="ohaeng">?</button>
        </div>
        <div class="sj-pentagon-wrap">${renderOhaengPentagon(a.elements_pct)}</div>
        <div class="sj-ohaeng-list">${cards}</div>
    `;
}

// ── 만세력 탭: 신강신약 ─────────────────────
function renderStrengthTab(r) {
    const s = r.analysis.strength;
    const pos = Math.round(s.score * 100);
    return `
        <div class="sj-gauge-wrap">
            <div class="sj-gauge-track">
                <div class="sj-gauge-marker" style="left:${pos}%;"></div>
            </div>
            <div class="sj-gauge-labels"><span>극신약</span><span>신약</span><span>중화</span><span>신강</span><span>극신강</span></div>
        </div>
        <div class="sj-strength-grade">${esc(s.grade)}</div>
        <div class="sj-strength-chips">
            <span class="sj-chip ${s.deukryeong ? 'on' : ''}">득령</span>
            <span class="sj-chip ${s.deukji ? 'on' : ''}">득지</span>
            <span class="sj-chip ${s.deukse ? 'on' : ''}">득세</span>
        </div>
        <div class="sj-strength-note">참고용 간이 판정이에요. 정확한 신강신약은 전문가 상담을 권해요.</div>
    `;
}

// ── 만세력 탭: 대운수 ────────────────────────
function luckItem(item, ageOrYear, isCurrent) {
    return `
        <div class="sj-luck-item ${isCurrent ? 'current' : ''}">
            <div class="sj-luck-age">${ageOrYear}</div>
            <div class="sj-luck-sipseong">${esc(item.sipseong_stem)}</div>
            <div class="sj-luck-stem" style="color:${EL_COLOR[item.stem_element]};">${esc(item.stem)}</div>
            <div class="sj-luck-branch" style="color:${EL_COLOR[item.branch_element]};">${esc(item.branch)}</div>
            <div class="sj-luck-sipseong">${esc(item.sipseong_branch)}</div>
            <div class="sj-luck-unseong">${esc(item.unseong12)}</div>
        </div>`;
}

function ageInYearsTraditional(birthDate, today) {
    let age = today.getFullYear() - birthDate.getFullYear();
    const hasHadBirthdayThisYear =
        today.getMonth() > birthDate.getMonth() ||
        (today.getMonth() === birthDate.getMonth() && today.getDate() >= birthDate.getDate());
    if (!hasHadBirthdayThisYear) age -= 1;
    return age;
}

function renderSeunSection(r) {
    const thisYear = new Date().getFullYear();
    const items = r.seun.map((p) => luckItem(p, p.year, p.year === thisYear)).join('');
    return `
        <div class="sj-manse-title" style="margin-top:22px;">세운(년운)</div>
        <div class="sj-luck-row">${items}</div>
    `;
}

function renderLuckTab(r) {
    const titleBar = `
        <div class="sj-manse-title" style="display:flex;align-items:center;gap:6px;">
            대운수 <button type="button" class="sj-help-btn" data-tooltip="daewoon">?</button>
        </div>`;
    if (!r.daewoon) {
        return `${titleBar}<div class="sj-empty-state">대운은 성별 정보가 있어야 계산돼요.</div>${renderSeunSection(r)}`;
    }
    const dw = r.daewoon;
    const birthDate = new Date(r.solar.year, r.solar.month - 1, r.solar.day);
    const currentAge = ageInYearsTraditional(birthDate, new Date());
    const items = dw.pillars.map((p) => {
        const isCurrent = currentAge >= p.age && currentAge < p.age + 10;
        return luckItem(p, p.age, isCurrent);
    }).join('');

    return `
        ${titleBar}
        <div class="sj-luck-header">대운수: ${dw.start_age} · ${esc(dw.direction)}</div>
        <div class="sj-luck-row">${items}</div>
        ${renderSeunSection(r)}
    `;
}

// ── 만세력 탭 바 ─────────────────────────────
const MANSE_TABS = [
    { key: 'wongook', label: '사주원국', render: renderWongookTab },
    { key: 'relations', label: '사주관계', render: renderRelationsTab },
    { key: 'ohaeng', label: '오행과 십성', render: renderOhaengTab },
    { key: 'strength', label: '신강신약', render: renderStrengthTab },
    { key: 'luck', label: '대운수', render: renderLuckTab },
];

function renderManseTabs(r) {
    const active = state.manseTab;
    const tabBtns = MANSE_TABS.map((t) =>
        `<button type="button" class="sj-manse-tab ${t.key === active ? 'active' : ''}" data-mansetab="${t.key}">${t.label}</button>`
    ).join('');
    const activeTab = MANSE_TABS.find((t) => t.key === active) || MANSE_TABS[0];
    return `
        <div class="sj-manse">
            <div class="sj-manse-tabs">${tabBtns}</div>
            <div class="sj-manse-panel">${activeTab.render(r)}</div>
        </div>
    `;
}

function renderResult() {
    const r = state.result;
    const day = r.pillars.day;
    const meta = STEMS[day.stem] || STEMS['갑'];
    const dayColor = EL_COLOR[meta.el];
    const glow = dayColor + '55';

    const di = gapjaIndex(day.stem, day.branch);
    const rarity = 4 + ((di * 7) % 14);

    // 오늘의 운세
    const now = new Date();
    const tdi = dayIndexAnchor(now.getFullYear(), now.getMonth() + 1, now.getDate());
    const score = 58 + ((tdi * 11 + di * 17) % 42);
    const todayLine = TODAY_LINES[tdi % TODAY_LINES.length];
    const deg = Math.round((score / 100) * 360);
    const todayRing = `conic-gradient(#D4B36A ${deg}deg, rgba(255,255,255,.08) ${deg}deg)`;

    // 생년월일 라인
    const inp = r.solar;
    const hourVal = document.getElementById('f-hour').value;
    const calLabel = state.cal === 'lunar' ? '음력(양력환산)' : '양력';
    let birthLine = `${calLabel} ${inp.year}년 ${inp.month}월 ${inp.day}일`;
    if (r.pillars.hour && hourVal !== 'unknown') {
        birthLine += ` · ${hourVal.replace('-', '–')}시`;
    }

    const rev = state.allRevealed;
    const pillarsHtml = [
        pillarCard('년주', r.pillars.year, !rev),
        pillarCard('월주', r.pillars.month, !rev),
        pillarCard('일주', r.pillars.day, false),
        pillarCard('시주', r.pillars.hour, !rev && !!r.pillars.hour),
    ].join('');

    const keywordsHtml = meta.kw.map((k) => `<span class="sj-keyword">${esc(k)}</span>`).join('');
    const pillarsHint = rev ? '하늘이 정한 네 개의 기둥' : '일주 외 세 기둥은 아직 잠겨 있어요';

    const html = `
        <div class="sj-birthline">${esc(birthLine)}</div>
        <div class="sj-origin">당신의 사주 원국</div>

        <div class="sj-hero">
            <div class="sj-hero-label">나를 상징하는 기둥 · 일주(日柱)</div>
            <div class="sj-day-wrap">
                <div class="sj-day-glow" style="background:radial-gradient(circle, ${glow} 0%, transparent 70%);"></div>
                <div class="sj-day-tile" style="border-color:${dayColor};">
                    <div class="sj-day-hanja" style="color:${dayColor}; text-shadow:0 0 26px ${glow};">${esc(day.hanja[0])}</div>
                    <div class="sj-day-kr">${esc(day.korean)}</div>
                </div>
            </div>
            <div class="sj-rarity">✦ 상위 ${rarity}% 희귀 일주</div>
            <div class="sj-dayname">${esc(meta.name)}</div>
            <div class="sj-keywords">${keywordsHtml}</div>
            <p class="sj-daydesc">${esc(meta.desc)}</p>
        </div>

        <div class="sj-divider"></div>

        <div class="sj-pillars-title">사주 네 기둥 (四柱)</div>
        <div class="sj-pillars-hint" id="pillars-hint">${pillarsHint}</div>
        <div class="sj-pillars" id="pillars-grid">${pillarsHtml}</div>
        ${rev ? '' : `<button type="button" class="sj-reveal-btn" data-reveal-all>🔒 나머지 세 기둥 열어보기</button>`}

        <div class="sj-divider"></div>

        <div class="sj-today">
            <div class="sj-today-ring">
                <div class="disc" style="background:${todayRing};"></div>
                <div class="inner">
                    <div class="sj-today-score">${score}</div>
                    <div class="sj-today-unit">점</div>
                </div>
            </div>
            <div style="flex:1;">
                <div class="sj-today-kicker">오늘의 운세</div>
                <div class="sj-today-line">${esc(todayLine)}</div>
            </div>
        </div>

        <div class="sj-divider"></div>

        ${renderManseTabs(r)}

        <div class="sj-report">
            <div class="sj-report-body">
                <div class="sj-report-title">심층 해석 리포트</div>
                <div class="sj-report-list">
                    <div>· 타고난 재물운과 직업 적성</div>
                    <div>· 나와 잘 맞는 일주 · 상극인 일주</div>
                    <div>· ${now.getFullYear()}년 대운과 세운의 흐름</div>
                    <div>· 연애·궁합에서 끌리는 유형</div>
                </div>
            </div>
            ${state.locked ? `
            <div class="sj-report-lock">
                <div class="ic">🔒</div>
                <div class="t1">친구에게 공유하면 열려요</div>
                <div class="t2">가장 궁금한 이야기는 여기 숨어 있어요</div>
                <button type="button" class="sj-unlock" data-unlock>공유하고 무료로 열기</button>
            </div>` : ''}
        </div>

        <div class="sj-share">
            <button type="button" class="sj-btn-gold" data-share-card>🎴 내 사주 카드 저장하기</button>
            <button type="button" class="sj-btn-ghost" data-go-gunghap>💞 친구랑 궁합 보기</button>
            <button type="button" class="sj-btn-text" data-action="home">다시 계산하기</button>
        </div>
        <div class="sj-toast" id="share-toast"></div>
    `;

    const el = document.getElementById('result');
    el.innerHTML = html;
    bindResultActions(el);
}

function bindResultActions(el) {
    el.querySelector('[data-reveal-all]')?.addEventListener('click', () => {
        state.allRevealed = true;
        renderResult();
    });
    el.querySelector('[data-unlock]')?.addEventListener('click', () => {
        state.locked = false;
        renderResult();
    });
    el.querySelector('[data-go-gunghap]')?.addEventListener('click', () => {
        window.location.href = '/gunghap';
    });
    el.querySelector('[data-share-card]')?.addEventListener('click', () => {
        toast('사주 카드 이미지 저장은 곧 제공될 예정이에요.');
    });
    el.querySelector('[data-action="home"]')?.addEventListener('click', goHome);

    el.querySelectorAll('[data-mansetab]').forEach((btn) => {
        btn.addEventListener('click', () => {
            state.manseTab = btn.dataset.mansetab;
            renderResult();
        });
    });
    el.querySelectorAll('[data-relsub]').forEach((btn) => {
        btn.addEventListener('click', () => {
            state.relSubtab = btn.dataset.relsub;
            renderResult();
        });
    });
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
