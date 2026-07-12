import os

import requests
from flask import Flask, Response, abort, jsonify, render_template, request, url_for

from content_pages import list_content, load_content
from saju import calculate_saju
from saju.compat import couple_compat, day_stem_pair_relation, team_compat, zodiac_of
from saju.date_neighborhoods import neighborhood_of
from saju.luck import current_luck_snapshot

app = Flask(__name__)

KAKAO_LOCAL_URL = 'https://dapi.kakao.com/v2/local/search/keyword.json'

# OG/Twitter Card 등 절대 URL이 필요한 메타태그에 쓰는 배포 주소.
# 커스텀 도메인으로 옮기면 Railway 환경변수 PUBLIC_BASE_URL만 바꾸면 된다.
PUBLIC_BASE_URL = os.environ.get(
    'PUBLIC_BASE_URL', 'https://lunar-ganzhi-calculator-production.up.railway.app'
).rstrip('/')


@app.context_processor
def inject_public_urls():
    def og_image_url(filename):
        return f"{PUBLIC_BASE_URL}{url_for('static', filename=f'og/{filename}')}"

    return {
        'public_base_url': PUBLIC_BASE_URL,
        'og_image_url': og_image_url,
    }


def _load_kakao_key():
    """카카오 REST API 키: 환경변수 → data.env 파일 순으로 찾는다."""
    key = os.environ.get('KAKAO_REST_API_KEY')
    if key:
        return key
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.env')
    try:
        with open(env_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('KAKAO_REST_API_KEY='):
                    value = line.split('=', 1)[1].strip()
                    if value:
                        return value
    except OSError:
        pass
    return None


def _parse_hour(hour_range):
    """'13-15' 형식 → 시작 시각. 'unknown'/파싱 실패는 None(시주 생략)."""
    if not hour_range or hour_range == 'unknown':
        return None
    try:
        return int(hour_range.split('-')[0])
    except ValueError:
        return None


def _parse_person(prefix, label):
    """폼에서 p1_/p2_ 접두사의 한 사람 입력을 파싱. (kwargs, name) 또는 에러 메시지."""
    form = request.form
    try:
        year = int(form[f'{prefix}year'])
        month = int(form[f'{prefix}month'])
        day = int(form[f'{prefix}day'])
    except (KeyError, ValueError):
        raise ValueError(f'{label}의 생년월일을 올바르게 입력해 주세요.')

    gender = form.get(f'{prefix}gender')
    if gender not in ('male', 'female'):
        raise ValueError(f'{label}의 성별을 선택해 주세요.')

    kwargs = {
        'hour': _parse_hour(form.get(f'{prefix}hour', 'unknown')),
        'is_lunar': form.get(f'{prefix}calendarType') == 'lunar',
        'is_leap_month': form.get(f'{prefix}leapMonth') == 'true',
        'gender': gender,
    }
    name = (form.get(f'{prefix}name') or '').strip() or label
    return (year, month, day), kwargs, name


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        year = int(request.form['year'])
        month = int(request.form['month'])
        day = int(request.form['day'])
    except (KeyError, ValueError):
        return jsonify({'error': '생년월일을 올바르게 입력해 주세요.'}), 400

    is_lunar = request.form.get('calendarType') == 'lunar'
    is_leap_month = request.form.get('leapMonth') == 'true'

    gender = request.form.get('gender')
    if gender not in ('male', 'female'):
        return jsonify({'error': '성별을 선택해 주세요.'}), 400

    hour = _parse_hour(request.form.get('hour', 'unknown'))

    try:
        result = calculate_saju(
            year, month, day, hour,
            is_lunar=is_lunar, is_leap_month=is_leap_month, gender=gender,
        )
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    return jsonify(result)


@app.route('/gunghap')
def gunghap_page():
    return render_template('gunghap.html')


@app.route('/gunghap/calculate', methods=['POST'])
def gunghap_calculate():
    mode = request.form.get('mode')
    if mode not in ('couple', 'friends'):
        return jsonify({'error': '연인/친구 모드를 선택해 주세요.'}), 400

    try:
        count = int(request.form.get('count', 2))
    except ValueError:
        count = 2
    count = max(2, min(count, 4))
    if mode == 'couple':
        count = 2  # 연인 모드는 항상 2인

    people = []
    try:
        for i in range(1, count + 1):
            (y, m, d), kw, name = _parse_person(f'p{i}_', f'{i}번째 사람')
            people.append({'y': y, 'm': m, 'd': d, 'kw': kw, 'name': name})
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    sajus = []
    for i, p in enumerate(people, start=1):
        try:
            sajus.append(calculate_saju(p['y'], p['m'], p['d'], **p['kw']))
        except ValueError as exc:
            return jsonify({'error': f"{i}번째 사람: {exc}"}), 400

    def _person(name, saju):
        return {
            'name': name,
            'zodiac': zodiac_of(saju),
            'day_pillar': saju['pillars']['day']['korean'],
            'day_pillar_hanja': saju['pillars']['day']['hanja'],
            'day_element': saju['pillars']['day']['stem_element'],
            'solar': saju['solar'],
            'elements': saju['elements'],
            'daewoon': saju['daewoon'],
        }

    persons = [_person(p['name'], s) for p, s in zip(people, sajus)]
    day_elements = [p['day_element'] for p in persons]

    if mode == 'couple':
        compat = couple_compat(sajus[0], sajus[1])
        compat_out = {
            'mode': 'couple',
            'score': compat['score'],
            'grade': compat['grade'],
            'factors': compat['factors'],
            'day_stem_relation': day_stem_pair_relation(day_elements[0], day_elements[1]),
        }
    else:
        team = team_compat(sajus)
        compat_out = {
            'mode': 'friends',
            'score': team['score'],
            'grade': team['grade'],
            'pairwise': team['pairwise'],
            'unique_day_elements': len(set(day_elements)),
        }

    return jsonify({
        'persons': persons,
        'compat': compat_out,
        'luck_snapshot': current_luck_snapshot(),
    })


@app.route('/gunghap/date-spots')
def gunghap_date_spots():
    """월운(이번 달) 오행 기준 데이트 동네 1곳 + 실시간(또는 폴백) 맛집·카페."""
    element = current_luck_snapshot()['wolun']['branch_element']
    nbh = neighborhood_of(element)

    key = _load_kakao_key()
    if key:
        try:
            food = _kakao_search(key, f"{nbh['name']} 맛집", 'FD6')
            cafe = _kakao_search(key, f"{nbh['name']} 카페", 'CE7')
            return jsonify({
                'sample': False,
                'neighborhood': {'element': element, 'name': nbh['name'], 'tag': nbh['tag'], 'why': nbh['why']},
                'food': food, 'cafe': cafe,
            })
        except requests.RequestException:
            pass  # 네트워크/키 오류 → 폴백으로 계속

    return jsonify({
        'sample': True,
        'neighborhood': {'element': element, 'name': nbh['name'], 'tag': nbh['tag'], 'why': nbh['why']},
        'places': nbh['places'],
        'notice': 'KAKAO_REST_API_KEY를 설정하면 실시간 맛집·카페 추천을 받을 수 있어요.',
    })


def _kakao_search(key, query, category_code):
    resp = requests.get(
        KAKAO_LOCAL_URL,
        headers={'Authorization': f'KakaoAK {key}'},
        params={'query': query, 'category_group_code': category_code, 'size': 5},
        timeout=5,
    )
    resp.raise_for_status()
    return [
        {
            'name': doc.get('place_name', ''),
            'category': (doc.get('category_name') or '').split(' > ')[-1],
            'address': doc.get('road_address_name') or doc.get('address_name', ''),
            'url': doc.get('place_url', ''),
        }
        for doc in resp.json().get('documents', [])
    ]


@app.route('/learn')
def learn_index():
    return render_template('learn_index.html', articles=list_content())


@app.route('/learn/<slug>')
def learn_article(slug):
    article = load_content(slug)
    if article is None:
        abort(404)
    related = [a for a in (load_content(s) for s in article['related']) if a]
    return render_template('learn.html', article=article, related=related)


@app.route('/privacy')
def privacy():
    return render_template('privacy.html')


@app.route('/sitemap.xml')
def sitemap():
    urls = [
        f"{PUBLIC_BASE_URL}{url_for('home')}",
        f"{PUBLIC_BASE_URL}{url_for('gunghap_page')}",
        f"{PUBLIC_BASE_URL}{url_for('learn_index')}",
        f"{PUBLIC_BASE_URL}{url_for('privacy')}",
    ]
    urls += [
        f"{PUBLIC_BASE_URL}{url_for('learn_article', slug=a['slug'])}"
        for a in list_content()
    ]
    xml = render_template('sitemap.xml', urls=urls)
    return Response(xml, mimetype='application/xml')


@app.route('/robots.txt')
def robots_txt():
    body = f"User-agent: *\nAllow: /\nSitemap: {PUBLIC_BASE_URL}/sitemap.xml\n"
    return Response(body, mimetype='text/plain')


if __name__ == '__main__':
    app.run(debug=True)
