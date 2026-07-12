/* ============================================================
   정보성 툴팁 바텀시트. plan/active/07-content-tooltips-monetization.md §3.1
   [data-tooltip="slug"]가 달린 요소를 클릭하면 TOOLTIPS[slug](tooltip-content.js)
   내용으로 시트가 열린다. 시트는 하나만 만들어 재사용한다.
   ============================================================ */
(function () {
    let backdropEl = null;
    let sheetEl = null;
    let lastFocused = null;

    function ensureSheet() {
        if (backdropEl) return;
        backdropEl = document.createElement('div');
        backdropEl.className = 'sj-sheet-backdrop';
        backdropEl.hidden = true;
        backdropEl.innerHTML = `
            <div class="sj-sheet" role="dialog" aria-modal="true" aria-labelledby="sj-sheet-title" tabindex="-1">
                <button type="button" class="sj-sheet-close" aria-label="닫기">&times;</button>
                <div class="sj-sheet-title" id="sj-sheet-title"></div>
                <ul class="sj-sheet-bullets"></ul>
                <div class="sj-ad-slot">광고 영역 (준비 중)</div>
                <a class="sj-sheet-learn" href="#">자세히 보기 →</a>
            </div>`;
        document.body.appendChild(backdropEl);
        sheetEl = backdropEl.querySelector('.sj-sheet');

        backdropEl.addEventListener('click', (e) => {
            if (e.target === backdropEl) closeTooltip();
        });
        backdropEl.querySelector('.sj-sheet-close').addEventListener('click', closeTooltip);
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !backdropEl.hidden) closeTooltip();
        });
    }

    function openTooltip(slug) {
        const data = typeof TOOLTIPS !== 'undefined' ? TOOLTIPS[slug] : null;
        if (!data) return;
        ensureSheet();

        sheetEl.querySelector('.sj-sheet-title').textContent = data.title;
        const ul = sheetEl.querySelector('.sj-sheet-bullets');
        ul.innerHTML = '';
        data.bullets.forEach((b) => {
            const li = document.createElement('li');
            li.textContent = b;
            ul.appendChild(li);
        });
        sheetEl.querySelector('.sj-sheet-learn').href = data.learnUrl;

        lastFocused = document.activeElement;
        backdropEl.hidden = false;
        document.body.style.overflow = 'hidden';
        requestAnimationFrame(() => backdropEl.classList.add('show'));
        sheetEl.focus();
    }

    function closeTooltip() {
        if (!backdropEl || backdropEl.hidden) return;
        backdropEl.classList.remove('show');
        document.body.style.overflow = '';
        setTimeout(() => { backdropEl.hidden = true; }, 200);
        if (lastFocused && typeof lastFocused.focus === 'function') lastFocused.focus();
    }

    window.openTooltip = openTooltip;
    window.closeTooltip = closeTooltip;

    document.body.addEventListener('click', (e) => {
        const trigger = e.target.closest('[data-tooltip]');
        if (trigger) {
            e.preventDefault();
            openTooltip(trigger.dataset.tooltip);
        }
    });
})();
