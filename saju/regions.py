"""오행 방위 → 서울 데이트 지역 매핑과 구별 명소 폴백 데이터.

오행 방위설(목=동, 화=남, 토=중앙, 금=서, 수=북)을 서울 자치구 위치에 적용했다.
폴백 명소는 카카오 API 키가 없을 때 쓰이며, 특정 상호가 아닌
공개적으로 잘 알려진 거리·공원·명소만 수록해 허위 정보를 피한다.
"""

from __future__ import annotations

ELEMENT_DIRECTION = {"목": "동", "화": "남", "토": "중앙", "금": "서", "수": "북"}

ELEMENT_DISTRICTS = {
    "목": ["성동구", "광진구", "강동구"],
    "화": ["강남구", "서초구", "관악구", "동작구"],
    "토": ["종로구", "중구", "용산구"],
    "금": ["마포구", "서대문구", "영등포구", "강서구"],
    "수": ["성북구", "강북구", "노원구", "은평구"],
}

# 구별 대표 데이트 명소 (카카오 키 없을 때 폴백)
DISTRICT_SPOTS = {
    "성동구": ["성수동 카페거리", "서울숲"],
    "광진구": ["커먼그라운드 일대", "뚝섬한강공원"],
    "강동구": ["광나루한강공원", "천호동 로데오거리"],
    "강남구": ["가로수길", "코엑스 별마당도서관"],
    "서초구": ["예술의전당", "반포한강공원 세빛섬"],
    "관악구": ["샤로수길", "낙성대공원"],
    "동작구": ["보라매공원", "노량진 수산시장 일대"],
    "종로구": ["익선동 한옥거리", "서촌 골목길"],
    "중구": ["을지로 힙지로 골목", "남산 산책로"],
    "용산구": ["경리단길", "용산가족공원"],
    "마포구": ["연남동 경의선숲길", "망원동 망리단길"],
    "서대문구": ["연희동 골목길", "안산자락길"],
    "영등포구": ["문래창작촌", "여의도한강공원"],
    "강서구": ["서울식물원", "마곡나루 일대"],
    "성북구": ["성북동 골목길", "북악스카이웨이 팔각정"],
    "강북구": ["북서울꿈의숲", "우이동 만남의광장 일대"],
    "노원구": ["경춘선숲길(공트럴파크)", "화랑대 철도공원"],
    "은평구": ["은평한옥마을", "불광천 산책로"],
}


def recommend_districts(complement_elements: list[str]) -> dict:
    """보완 오행 목록 → 추천 방위·구 목록.

    반환: {'elements', 'directions', 'districts': [{'name','spots'}]}
    """
    directions = []
    districts = []
    seen = set()
    for el in complement_elements:
        directions.append(ELEMENT_DIRECTION[el])
        for name in ELEMENT_DISTRICTS[el]:
            if name not in seen:
                seen.add(name)
                districts.append({"name": name, "spots": DISTRICT_SPOTS[name]})
    return {
        "elements": complement_elements,
        "directions": directions,
        "districts": districts,
    }
