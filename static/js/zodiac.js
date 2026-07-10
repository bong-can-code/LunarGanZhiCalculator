/**
 * 십이간지 귀여운 SVG 캐릭터.
 * 공통 스타일: 둥근 얼굴 + 점 눈 + 볼터치, 동물별 귀/뿔/무늬로 차별화.
 * 모든 리소스가 인라인이라 캔버스(drawImage)에서도 안전하게 쓸 수 있다.
 */

const ZODIAC_STYLES = {
    '쥐': { color: '#b0bec5', build: ratFeatures },
    '소': { color: '#efdcc3', build: oxFeatures },
    '호랑이': { color: '#ffb74d', build: tigerFeatures },
    '토끼': { color: '#f8f4f0', build: rabbitFeatures },
    '용': { color: '#81c784', build: dragonFeatures },
    '뱀': { color: '#aed581', build: snakeFeatures },
    '말': { color: '#bcaaa4', build: horseFeatures },
    '양': { color: '#f5f0e6', build: sheepFeatures },
    '원숭이': { color: '#c8a27a', build: monkeyFeatures },
    '닭': { color: '#fff3e0', build: roosterFeatures },
    '개': { color: '#d7ccc8', build: dogFeatures },
    '돼지': { color: '#f8bbd0', build: pigFeatures },
};

/** 동물 이름 → 120x120 viewBox SVG 문자열 */
function zodiacCharacterSVG(animal) {
    const style = ZODIAC_STYLES[animal] || ZODIAC_STYLES['쥐'];
    const { back = '', front = '' } = style.build(style.color);
    return `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120">
  ${back}
  <circle cx="60" cy="66" r="38" fill="${style.color}" stroke="#5d4037" stroke-width="2.5"/>
  ${front}
  <circle cx="47" cy="62" r="4" fill="#3e2723"/>
  <circle cx="73" cy="62" r="4" fill="#3e2723"/>
  <circle cx="48.5" cy="60.5" r="1.3" fill="#fff"/>
  <circle cx="74.5" cy="60.5" r="1.3" fill="#fff"/>
  <circle cx="40" cy="74" r="5.5" fill="#f48fb1" opacity="0.55"/>
  <circle cx="80" cy="74" r="5.5" fill="#f48fb1" opacity="0.55"/>
  <path d="M 55 76 Q 60 81 65 76" fill="none" stroke="#3e2723" stroke-width="2.5" stroke-linecap="round"/>
</svg>`;
}

function ratFeatures(color) {
    return {
        back: `
            <circle cx="28" cy="34" r="15" fill="${color}" stroke="#5d4037" stroke-width="2.5"/>
            <circle cx="92" cy="34" r="15" fill="${color}" stroke="#5d4037" stroke-width="2.5"/>
            <circle cx="28" cy="34" r="8" fill="#f8bbd0"/>
            <circle cx="92" cy="34" r="8" fill="#f8bbd0"/>`,
        front: `<ellipse cx="60" cy="72" rx="4" ry="3" fill="#f48fb1"/>`,
    };
}

function oxFeatures(color) {
    return {
        back: `
            <path d="M 24 42 Q 8 34 12 18 Q 26 24 32 36 Z" fill="#eceff1" stroke="#5d4037" stroke-width="2.5"/>
            <path d="M 96 42 Q 112 34 108 18 Q 94 24 88 36 Z" fill="#eceff1" stroke="#5d4037" stroke-width="2.5"/>
            <ellipse cx="26" cy="52" rx="10" ry="6" fill="${color}" stroke="#5d4037" stroke-width="2.5" transform="rotate(-25 26 52)"/>
            <ellipse cx="94" cy="52" rx="10" ry="6" fill="${color}" stroke="#5d4037" stroke-width="2.5" transform="rotate(25 94 52)"/>`,
        front: `
            <ellipse cx="60" cy="80" rx="13" ry="9" fill="#f8bbd0" opacity="0.8"/>
            <circle cx="55" cy="80" r="1.8" fill="#5d4037"/>
            <circle cx="65" cy="80" r="1.8" fill="#5d4037"/>`,
    };
}

function tigerFeatures(color) {
    return {
        back: `
            <circle cx="32" cy="36" r="11" fill="${color}" stroke="#5d4037" stroke-width="2.5"/>
            <circle cx="88" cy="36" r="11" fill="${color}" stroke="#5d4037" stroke-width="2.5"/>
            <circle cx="32" cy="36" r="5" fill="#ffe0b2"/>
            <circle cx="88" cy="36" r="5" fill="#ffe0b2"/>`,
        front: `
            <path d="M 56 34 L 60 42 L 64 34" fill="none" stroke="#5d4037" stroke-width="3" stroke-linecap="round"/>
            <path d="M 44 40 L 48 47" stroke="#5d4037" stroke-width="3" stroke-linecap="round"/>
            <path d="M 76 40 L 72 47" stroke="#5d4037" stroke-width="3" stroke-linecap="round"/>
            <ellipse cx="60" cy="72" rx="4.5" ry="3.5" fill="#5d4037"/>`,
    };
}

function rabbitFeatures(color) {
    return {
        back: `
            <ellipse cx="42" cy="20" rx="9" ry="24" fill="${color}" stroke="#5d4037" stroke-width="2.5" transform="rotate(-8 42 20)"/>
            <ellipse cx="78" cy="20" rx="9" ry="24" fill="${color}" stroke="#5d4037" stroke-width="2.5" transform="rotate(8 78 20)"/>
            <ellipse cx="42" cy="22" rx="4" ry="16" fill="#f8bbd0" transform="rotate(-8 42 22)"/>
            <ellipse cx="78" cy="22" rx="4" ry="16" fill="#f8bbd0" transform="rotate(8 78 22)"/>`,
        front: `<ellipse cx="60" cy="71" rx="3.5" ry="2.8" fill="#f48fb1"/>`,
    };
}

function dragonFeatures(color) {
    return {
        back: `
            <path d="M 38 36 Q 30 16 20 14 Q 28 30 34 40 Z" fill="#fff9c4" stroke="#5d4037" stroke-width="2.5"/>
            <path d="M 82 36 Q 90 16 100 14 Q 92 30 86 40 Z" fill="#fff9c4" stroke="#5d4037" stroke-width="2.5"/>
            <circle cx="26" cy="52" r="7" fill="${color}" stroke="#5d4037" stroke-width="2.5"/>
            <circle cx="94" cy="52" r="7" fill="${color}" stroke="#5d4037" stroke-width="2.5"/>`,
        front: `
            <path d="M 48 38 Q 60 30 72 38" fill="none" stroke="#388e3c" stroke-width="4" stroke-linecap="round"/>
            <ellipse cx="60" cy="72" rx="5" ry="3.5" fill="#388e3c" opacity="0.7"/>`,
    };
}

function snakeFeatures(color) {
    return {
        back: `
            <path d="M 60 104 Q 30 112 24 96 Q 40 100 52 96" fill="${color}" stroke="#5d4037" stroke-width="2.5"/>`,
        front: `
            <path d="M 60 78 L 60 86 M 57 86 L 60 83 L 63 86" fill="none" stroke="#e53935" stroke-width="2" stroke-linecap="round"/>
            <circle cx="52" cy="44" r="2" fill="#7cb342"/>
            <circle cx="68" cy="44" r="2" fill="#7cb342"/>
            <circle cx="60" cy="38" r="2" fill="#7cb342"/>`,
    };
}

function horseFeatures(color) {
    return {
        back: `
            <ellipse cx="36" cy="30" rx="8" ry="14" fill="${color}" stroke="#5d4037" stroke-width="2.5" transform="rotate(-15 36 30)"/>
            <ellipse cx="84" cy="30" rx="8" ry="14" fill="${color}" stroke="#5d4037" stroke-width="2.5" transform="rotate(15 84 30)"/>
            <path d="M 48 30 Q 60 18 72 30 L 70 44 Q 60 36 50 44 Z" fill="#8d6e63" stroke="#5d4037" stroke-width="2.5"/>`,
        front: `
            <ellipse cx="60" cy="79" rx="11" ry="8" fill="#efebe9" opacity="0.9"/>
            <circle cx="56" cy="79" r="1.7" fill="#5d4037"/>
            <circle cx="64" cy="79" r="1.7" fill="#5d4037"/>`,
    };
}

function sheepFeatures(color) {
    return {
        back: `
            <circle cx="38" cy="34" r="10" fill="#fff" stroke="#5d4037" stroke-width="2.5"/>
            <circle cx="60" cy="28" r="11" fill="#fff" stroke="#5d4037" stroke-width="2.5"/>
            <circle cx="82" cy="34" r="10" fill="#fff" stroke="#5d4037" stroke-width="2.5"/>
            <path d="M 28 46 Q 16 46 18 34 Q 28 36 32 42 Z" fill="#e0cda9" stroke="#5d4037" stroke-width="2.5"/>
            <path d="M 92 46 Q 104 46 102 34 Q 92 36 88 42 Z" fill="#e0cda9" stroke="#5d4037" stroke-width="2.5"/>`,
        front: `<ellipse cx="60" cy="71" rx="3.5" ry="2.8" fill="#f48fb1"/>`,
    };
}

function monkeyFeatures(color) {
    return {
        back: `
            <circle cx="26" cy="58" r="11" fill="${color}" stroke="#5d4037" stroke-width="2.5"/>
            <circle cx="94" cy="58" r="11" fill="${color}" stroke="#5d4037" stroke-width="2.5"/>
            <circle cx="26" cy="58" r="5.5" fill="#f3e0ce"/>
            <circle cx="94" cy="58" r="5.5" fill="#f3e0ce"/>`,
        front: `
            <path d="M 34 56 Q 34 40 48 38 Q 60 30 72 38 Q 86 40 86 56 Q 74 48 60 48 Q 46 48 34 56 Z" fill="#f3e0ce"/>
            <ellipse cx="60" cy="74" rx="9" ry="6" fill="#f3e0ce"/>
            <circle cx="47" cy="62" r="4" fill="#3e2723"/>
            <circle cx="73" cy="62" r="4" fill="#3e2723"/>`,
    };
}

function roosterFeatures(color) {
    return {
        back: `
            <circle cx="49" cy="24" r="7" fill="#ef5350" stroke="#5d4037" stroke-width="2.5"/>
            <circle cx="60" cy="19" r="8" fill="#ef5350" stroke="#5d4037" stroke-width="2.5"/>
            <circle cx="71" cy="24" r="7" fill="#ef5350" stroke="#5d4037" stroke-width="2.5"/>`,
        front: `
            <path d="M 54 70 L 60 78 L 66 70 Z" fill="#ffb300" stroke="#5d4037" stroke-width="2"/>
            <path d="M 58 82 Q 60 86 62 82" fill="#ef5350"/>`,
    };
}

function dogFeatures(color) {
    return {
        back: `
            <ellipse cx="30" cy="44" rx="10" ry="17" fill="#8d6e63" stroke="#5d4037" stroke-width="2.5" transform="rotate(18 30 44)"/>
            <ellipse cx="90" cy="44" rx="10" ry="17" fill="#8d6e63" stroke="#5d4037" stroke-width="2.5" transform="rotate(-18 90 44)"/>`,
        front: `
            <ellipse cx="60" cy="76" rx="10" ry="7" fill="#fff" opacity="0.85"/>
            <ellipse cx="60" cy="72" rx="4.5" ry="3.5" fill="#3e2723"/>
            <circle cx="73" cy="52" r="6" fill="#8d6e63" opacity="0.6"/>`,
    };
}

function pigFeatures(color) {
    return {
        back: `
            <path d="M 34 40 L 28 24 L 44 32 Z" fill="${color}" stroke="#5d4037" stroke-width="2.5"/>
            <path d="M 86 40 L 92 24 L 76 32 Z" fill="${color}" stroke="#5d4037" stroke-width="2.5"/>`,
        front: `
            <ellipse cx="60" cy="74" rx="9" ry="7" fill="#f48fb1" stroke="#5d4037" stroke-width="2"/>
            <circle cx="56.5" cy="74" r="1.8" fill="#5d4037"/>
            <circle cx="63.5" cy="74" r="1.8" fill="#5d4037"/>`,
    };
}

/** 커플 러브 씬: 두 캐릭터 + 하트. 320x180 viewBox SVG */
function coupleSceneSVG(animal1, animal2) {
    const c1 = zodiacCharacterSVG(animal1)
        .replace('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120">', '')
        .replace('</svg>', '');
    const c2 = zodiacCharacterSVG(animal2)
        .replace('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120">', '')
        .replace('</svg>', '');
    return `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 180">
  <defs>
    <linearGradient id="loveBg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#ffe3ec"/>
      <stop offset="1" stop-color="#e3f0ff"/>
    </linearGradient>
  </defs>
  <rect width="320" height="180" rx="16" fill="url(#loveBg)"/>
  <path d="M 160 74 C 152 62 134 64 134 78 C 134 90 152 100 160 106 C 168 100 186 90 186 78 C 186 64 168 62 160 74 Z" fill="#ef5350" stroke="#c62828" stroke-width="2"/>
  <path d="M 120 34 C 117 29 110 30 110 36 C 110 40 117 44 120 47 C 123 44 130 40 130 36 C 130 30 123 29 120 34 Z" fill="#f48fb1" opacity="0.8"/>
  <path d="M 206 26 C 203 21 196 22 196 28 C 196 32 203 36 206 39 C 209 36 216 32 216 28 C 216 22 209 21 206 26 Z" fill="#f48fb1" opacity="0.8"/>
  <g transform="translate(10, 30) scale(1.05)">${c1}</g>
  <g transform="translate(184, 30) scale(1.05)">${c2}</g>
</svg>`;
}
