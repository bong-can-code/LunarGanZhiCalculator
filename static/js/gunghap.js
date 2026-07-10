let lastResult = null;

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('gunghap-form');

    // 사람별 음력 선택 시 윤달 체크박스 표시/숨김
    form.addEventListener('change', (event) => {
        const name = event.target.name || '';
        const match = name.match(/^(p\d)_calendarType$/);
        if (match) {
            const wrap = form.querySelector(`.leap-wrap[data-prefix="${match[1]}"]`);
            if (wrap) wrap.style.display = event.target.value === 'lunar' ? '' : 'none';
        }
    });

    form.addEventListener('submit', (event) => {
        event.preventDefault();
        submitGunghap();
    });
});

async function submitGunghap() {
    const resultEl = document.getElementById('result');
    const formData = new FormData(document.getElementById('gunghap-form'));

    resultEl.textContent = '궁합을 보는 중...';

    try {
        const response = await fetch('/gunghap/calculate', { method: 'POST', body: formData });
        const data = await response.json();

        if (!response.ok) {
            renderError(data.error || '계산 중 오류가 발생했습니다.');
            return;
        }

        lastResult = data;
        renderGunghap(data);
    } catch (err) {
        renderError('서버와 통신할 수 없습니다.');
    }
}

function renderError(message) {
    document.getElementById('result').innerHTML =
        `<p class="error">${escapeHtml(message)}</p>`;
}

function renderGunghap(data) {
    const resultEl = document.getElementById('result');
    const [p1, p2] = data.persons;
    const { score, grade, factors } = data.compat;
    const rec = data.recommendation;

    const elementsLabel = rec.elements.join('·');
    const directionsLabel = [...new Set(rec.directions)]
        .map((d) => (d === '중앙' ? '중심부' : `${d}쪽`))
        .join('·');

    resultEl.innerHTML = `
        <div class="couple-scene">${coupleSceneSVG(p1.zodiac.animal, p2.zodiac.animal)}</div>
        <p class="couple-names">
            ${escapeHtml(p1.name)} (${p1.zodiac.animal}띠) 💕 ${escapeHtml(p2.name)} (${p2.zodiac.animal}띠)
        </p>

        <div class="score-wrap">
            <div class="score-circle" style="--score:${score}">
                <div class="inner">
                    <span class="score-number">${score}</span>
                    <span class="score-unit">점</span>
                </div>
            </div>
            <p class="score-grade">${escapeHtml(grade)}</p>
        </div>

        ${renderFactors(factors)}

        <h3>💘 추천 데이트 지역</h3>
        <p class="element-summary">
            두 분에게 필요한 기운은 <strong>${escapeHtml(elementsLabel)}</strong> —
            서울 <strong>${escapeHtml(directionsLabel)}</strong> 데이트를 추천해요!
        </p>
        <div class="district-chips">
            ${rec.districts.map((d, i) => `
                <button type="button" class="district-chip ${i === 0 ? 'active' : ''}"
                        data-district="${escapeHtml(d.name)}">${escapeHtml(d.name)}</button>
            `).join('')}
        </div>
        <div id="places"></div>

        <div class="share-buttons">
            <button type="button" class="secondary" id="save-image-btn">🖼 이미지 저장</button>
            <button type="button" class="insta" id="insta-share-btn">📸 인스타그램 공유</button>
        </div>
        <p class="share-toast" id="share-toast"></p>
        <canvas id="share-canvas" width="1080" height="1080"></canvas>
    `;

    resultEl.querySelectorAll('.district-chip').forEach((chip) => {
        chip.addEventListener('click', () => {
            resultEl.querySelectorAll('.district-chip').forEach((c) => c.classList.remove('active'));
            chip.classList.add('active');
            loadPlaces(chip.dataset.district);
        });
    });

    document.getElementById('save-image-btn').addEventListener('click', () => shareImage(false));
    document.getElementById('insta-share-btn').addEventListener('click', () => shareImage(true));

    if (rec.districts.length > 0) {
        loadPlaces(rec.districts[0].name);
    }
}

function renderFactors(factors) {
    if (!factors.length) {
        return `<h3>🔍 궁합 풀이</h3>
            <p class="element-summary">특별한 합·충 없이 무난하게 어울리는 조합이에요.</p>`;
    }
    const items = factors.map((f) => `
        <li>
            <span class="factor-delta ${f.delta >= 0 ? 'plus' : 'minus'}">
                ${f.delta >= 0 ? '+' : ''}${f.delta}
            </span>
            <span>
                <span class="factor-label">${escapeHtml(f.label)}</span><br>
                <span class="factor-desc">${escapeHtml(f.desc)}</span>
            </span>
        </li>`).join('');
    return `<h3>🔍 궁합 풀이</h3><ul class="factor-list">${items}</ul>`;
}

async function loadPlaces(district) {
    const placesEl = document.getElementById('places');
    placesEl.innerHTML = '<p class="element-summary">장소를 찾는 중...</p>';

    try {
        const response = await fetch(`/gunghap/places?district=${encodeURIComponent(district)}`);
        const data = await response.json();

        if (!response.ok) {
            placesEl.innerHTML = `<p class="error">${escapeHtml(data.error || '장소를 불러오지 못했습니다.')}</p>`;
            return;
        }

        if (data.sample) {
            placesEl.innerHTML = `
                <ul class="spot-list">
                    ${data.spots.map((s) => `<li>📍 ${escapeHtml(s)} <span class="factor-desc">— ${escapeHtml(district)} 인기 데이트 명소</span></li>`).join('')}
                </ul>
                <div class="sample-notice">ℹ️ ${escapeHtml(data.notice)}</div>
            `;
            return;
        }

        placesEl.innerHTML = `
            <div class="places-grid">
                ${renderPlaceColumn('🍽 식당', data.food)}
                ${renderPlaceColumn('☕ 카페', data.cafe)}
            </div>
        `;
    } catch (err) {
        placesEl.innerHTML = '<p class="error">장소를 불러오지 못했습니다.</p>';
    }
}

function renderPlaceColumn(title, places) {
    if (!places || !places.length) {
        return `<div class="places-col"><h4>${title}</h4>
            <p class="factor-desc">검색 결과가 없어요.</p></div>`;
    }
    const items = places.map((p) => `
        <div class="place-item">
            <div class="name">${escapeHtml(p.name)}</div>
            <div class="meta">${escapeHtml(p.category)} · ${escapeHtml(p.address)}</div>
            ${p.url ? `<a href="${escapeHtml(p.url)}" target="_blank" rel="noopener">카카오맵에서 보기 →</a>` : ''}
        </div>`).join('');
    return `<div class="places-col"><h4>${title}</h4>${items}</div>`;
}

/* ── 공유 이미지 (1080x1080 인스타 정방형) ─────────────────── */

function svgToImage(svgString) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = reject;
        img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgString);
    });
}

async function buildShareCanvas() {
    const canvas = document.getElementById('share-canvas');
    const ctx = canvas.getContext('2d');
    const [p1, p2] = lastResult.persons;
    const { score, grade } = lastResult.compat;
    const rec = lastResult.recommendation;

    // 배경 그라데이션
    const bg = ctx.createLinearGradient(0, 0, 1080, 1080);
    bg.addColorStop(0, '#ffe3ec');
    bg.addColorStop(1, '#e3f0ff');
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, 1080, 1080);

    // 흰색 카드
    roundRect(ctx, 60, 60, 960, 960, 48);
    ctx.fillStyle = 'rgba(255,255,255,0.92)';
    ctx.fill();

    ctx.textAlign = 'center';
    ctx.fillStyle = '#1d1d1f';
    ctx.font = 'bold 52px -apple-system, "Malgun Gothic", sans-serif';
    ctx.fillText('십이간지 커플 궁합', 540, 170);

    // 커플 씬
    const scene = await svgToImage(coupleSceneSVG(p1.zodiac.animal, p2.zodiac.animal));
    ctx.drawImage(scene, 140, 220, 800, 450);

    // 이름
    ctx.font = '38px -apple-system, "Malgun Gothic", sans-serif';
    ctx.fillStyle = '#5f6368';
    ctx.fillText(
        `${p1.name} (${p1.zodiac.animal}띠)  ♥  ${p2.name} (${p2.zodiac.animal}띠)`,
        540, 730,
    );

    // 점수 + 등급
    ctx.font = 'bold 130px -apple-system, "Malgun Gothic", sans-serif';
    ctx.fillStyle = '#ff5f8f';
    ctx.fillText(`${score}점`, 540, 880);
    ctx.font = 'bold 46px -apple-system, "Malgun Gothic", sans-serif';
    ctx.fillStyle = '#1d1d1f';
    ctx.fillText(grade, 540, 945);

    // 추천 지역 한 줄
    const firstDistrict = rec.districts.length ? rec.districts[0].name : '';
    ctx.font = '30px -apple-system, "Malgun Gothic", sans-serif';
    ctx.fillStyle = '#86868b';
    ctx.fillText(`추천 데이트 지역: ${firstDistrict} 외 ${Math.max(rec.districts.length - 1, 0)}곳`, 540, 990);

    return canvas;
}

function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
}

async function shareImage(preferShare) {
    const toast = document.getElementById('share-toast');
    if (!lastResult) return;

    toast.textContent = '이미지를 만드는 중...';
    try {
        const canvas = await buildShareCanvas();
        const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/png'));
        const file = new File([blob], 'gunghap.png', { type: 'image/png' });

        if (preferShare && navigator.canShare && navigator.canShare({ files: [file] })) {
            await navigator.share({
                files: [file],
                title: '십이간지 커플 궁합',
                text: `우리 궁합은 ${lastResult.compat.score}점! ${lastResult.compat.grade} 💕`,
            });
            toast.textContent = '공유 시트에서 인스타그램을 선택해 주세요!';
            return;
        }

        // 다운로드 폴백
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'gunghap.png';
        link.click();
        URL.revokeObjectURL(link.href);
        toast.textContent = preferShare
            ? '이미지를 저장했어요. 인스타그램 앱에서 업로드해 주세요! 📸'
            : '이미지를 저장했어요!';
    } catch (err) {
        if (err && err.name === 'AbortError') {
            toast.textContent = '';
            return;
        }
        toast.textContent = '이미지 생성에 실패했어요. 다시 시도해 주세요.';
    }
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = String(str);
    return div.innerHTML;
}
