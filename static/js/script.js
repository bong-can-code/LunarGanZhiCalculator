document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('date-form');
    const leapWrap = document.getElementById('leapWrap');

    // 달력 유형에 따라 윤달 체크박스 표시/숨김
    form.addEventListener('change', (event) => {
        if (event.target.name === 'calendarType') {
            leapWrap.style.display = event.target.value === 'lunar' ? '' : 'none';
        }
    });

    // 폼 제출 처리
    form.addEventListener('submit', (event) => {
        event.preventDefault();
        submitForm();
    });
});

const PILLAR_ORDER = ['hour', 'day', 'month', 'year'];
const PILLAR_LABELS = { year: '년주', month: '월주', day: '일주', hour: '시주' };
const ELEMENT_ORDER = ['목', '화', '토', '금', '수'];
const EXTRA_INFO_BUTTONS = [
    { key: 'sipseong', label: '십성' },
    { key: 'sinsal', label: '신살' },
    { key: 'unseong12', label: '12운성' },
    { key: 'hyeongchung', label: '형충회합' },
];

// 제출 함수
async function submitForm() {
    const resultEl = document.getElementById('result');
    const formData = new FormData(document.getElementById('date-form'));

    resultEl.textContent = '계산 중...';

    try {
        const response = await fetch('/calculate', { method: 'POST', body: formData });
        const data = await response.json();

        if (!response.ok) {
            renderError(data.error || '계산 중 오류가 발생했습니다.');
            return;
        }

        renderResult(data);
    } catch (err) {
        renderError('서버와 통신할 수 없습니다.');
    }
}

function renderError(message) {
    const resultEl = document.getElementById('result');
    resultEl.innerHTML = `<p class="error">${escapeHtml(message)}</p>`;
}

function renderResult(data) {
    const resultEl = document.getElementById('result');
    const { solar, lunar, pillars, elements, daewoon, seun } = data;

    const solarStr = `${solar.year}-${String(solar.month).padStart(2, '0')}-${String(solar.day).padStart(2, '0')}`;
    const birthDate = new Date(solar.year, solar.month - 1, solar.day);

    resultEl.innerHTML = `
        <p>양력: ${solarStr} / 음력: ${escapeHtml(lunar)}</p>
        ${renderPillarGrid(pillars)}
        ${renderElementSummary(elements)}
        ${renderExtraInfoButtons()}
        ${daewoon ? renderDaewoon(daewoon, birthDate) : ''}
        ${renderSeun(seun)}
    `;

    bindExtraInfoButtons(resultEl);
}

function renderPillarGrid(pillars) {
    const cols = PILLAR_ORDER.map((key) => {
        const p = pillars[key];
        if (!p) {
            return `
                <div class="pillar-col">
                    <div class="pillar-label">${PILLAR_LABELS[key]}</div>
                    <div class="tile-stack"><div class="tile unknown">시간 모름</div></div>
                </div>`;
        }
        return `
            <div class="pillar-col">
                <div class="pillar-label">${PILLAR_LABELS[key]} (${escapeHtml(p.hanja)})</div>
                <div class="tile-stack">
                    <div class="tile element-${p.stem_element}">${escapeHtml(p.stem)}<br>${escapeHtml(stemHanja(p))}</div>
                    <div class="tile element-${p.branch_element}">${escapeHtml(p.branch)}<br>${escapeHtml(branchHanja(p))}</div>
                </div>
                <div class="hidden-stems">${p.hidden_stems.join(' ')}</div>
                <div class="nayin">${escapeHtml(p.nayin.korean)} (${escapeHtml(p.nayin.hanja)})</div>
            </div>`;
    }).join('');

    return `<div class="pillar-grid">${cols}</div>`;
}

function stemHanja(p) {
    return p.hanja[0];
}

function branchHanja(p) {
    return p.hanja[1];
}

function renderElementSummary(elements) {
    const parts = ELEMENT_ORDER.map((el) => `${el} ${elements[el]}`).join(', ');
    return `<p class="element-summary">오행: ${parts}</p>`;
}

function renderExtraInfoButtons() {
    const buttons = EXTRA_INFO_BUTTONS.map((b) => `
        <label class="inline">
            <input type="checkbox" class="extra-info-toggle" data-key="${b.key}"> ${b.label}
        </label>`).join('');
    const notes = EXTRA_INFO_BUTTONS.map((b) => `
        <p class="extra-info-note" data-key="${b.key}" style="display:none;">
            ${b.label} 계산은 아직 지원하지 않습니다. (준비 중)
        </p>`).join('');
    return `<div class="extra-info">${buttons}${notes}</div>`;
}

function bindExtraInfoButtons(container) {
    container.querySelectorAll('.extra-info-toggle').forEach((checkbox) => {
        checkbox.addEventListener('change', () => {
            const note = container.querySelector(`.extra-info-note[data-key="${checkbox.dataset.key}"]`);
            if (note) note.style.display = checkbox.checked ? '' : 'none';
        });
    });
}

function renderDaewoon(daewoon, birthDate) {
    const currentAge = ageInYears(birthDate, new Date());
    const items = daewoon.pillars.map((p) => {
        const isCurrent = currentAge >= p.age && currentAge < p.age + 10;
        return `
            <div class="luck-item ${isCurrent ? 'current' : ''}">
                <div class="luck-age">${p.age}</div>
                <div class="tile-stack">
                    <div class="tile element-${p.stem_element}">${escapeHtml(p.stem)}</div>
                    <div class="tile element-${p.branch_element}">${escapeHtml(p.branch)}</div>
                </div>
            </div>`;
    }).join('');

    return `
        <h3>전통나이(대운수: ${daewoon.start_age}, ${daewoon.direction})</h3>
        <div class="luck-row">${items}</div>`;
}

function renderSeun(seun) {
    const thisYear = new Date().getFullYear();
    const items = seun.map((p) => {
        const isCurrent = p.year === thisYear;
        return `
            <div class="luck-item ${isCurrent ? 'current' : ''}">
                <div class="luck-age">${p.year}</div>
                <div class="tile-stack">
                    <div class="tile element-${p.stem_element}">${escapeHtml(p.stem)}</div>
                    <div class="tile element-${p.branch_element}">${escapeHtml(p.branch)}</div>
                </div>
            </div>`;
    }).join('');

    return `
        <h3>세운(년운)</h3>
        <div class="luck-row">${items}</div>`;
}

function ageInYears(birthDate, today) {
    let age = today.getFullYear() - birthDate.getFullYear();
    const hasHadBirthdayThisYear =
        today.getMonth() > birthDate.getMonth() ||
        (today.getMonth() === birthDate.getMonth() && today.getDate() >= birthDate.getDate());
    if (!hasHadBirthdayThisYear) age -= 1;
    return age;
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
