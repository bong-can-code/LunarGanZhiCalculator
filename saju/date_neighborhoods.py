"""이 달의 데이트 동네: 월운(月運) 오행 → 서울 동네 1곳 + 폴백 장소.

지금 이 순간의 월운 오행에 어울리는 트렌디한 동네 1곳을 추천한다(달력 기반이라
방문 시점이 같으면 누구에게나 같은 동네가 나오고, 매달 새로 확인하고 싶어지는 훅이 된다).

궁합 자체에서 "두 사람에게 부족한 오행"을 계산하는 로직(couple_compat의
complement_elements)과는 다른, 별개의 추천 축이다.

폴백 장소는 카카오 API 키가 없을 때 쓰이며, 실존하는 잘 알려진 상호만 수록했다.
"""

from __future__ import annotations

NEIGHBORHOODS = {
    "목": {
        "name": "연남동",
        "tag": "초록 골목",
        "why": "나무의 기운이 흐르는 연남동. 골목을 따라 걷다 보면 마음도 자연스레 자라나요.",
        "places": [
            {"name": "연남살롱", "category": "카페", "address": "서울 마포구 연남동", "url": ""},
            {"name": "툭툭누들타이", "category": "맛집", "address": "서울 마포구 연남동", "url": ""},
            {"name": "연남방앗간", "category": "디저트", "address": "서울 마포구 연남동", "url": ""},
        ],
    },
    "화": {
        "name": "이태원 경리단길",
        "tag": "열정의 언덕",
        "why": "불의 기운이 강한 이번 달, 활기 넘치는 경리단길에서 설렘이 한층 뜨거워져요.",
        "places": [
            {"name": "펠트커피 이태원", "category": "카페", "address": "서울 용산구 이태원동", "url": ""},
            {"name": "부자피자", "category": "맛집", "address": "서울 용산구 이태원동", "url": ""},
            {"name": "오리올", "category": "다이닝", "address": "서울 용산구 이태원동", "url": ""},
        ],
    },
    "토": {
        "name": "북촌·삼청동",
        "tag": "고즈넉한 안정",
        "why": "흙의 기운이 차분히 감싸는 달. 한옥길을 천천히 걸으며 서로에게 안정을 주기 좋아요.",
        "places": [
            {"name": "슬로우가든", "category": "카페", "address": "서울 종로구 삼청동", "url": ""},
            {"name": "눈나무집", "category": "맛집", "address": "서울 종로구 삼청동", "url": ""},
            {"name": "북촌손만두", "category": "맛집", "address": "서울 종로구 북촌", "url": ""},
        ],
    },
    "금": {
        "name": "한남동",
        "tag": "세련된 취향",
        "why": "금의 기운이 빛나는 달. 감각적인 한남동 거리에서 취향을 맞춰보기 좋은 시기예요.",
        "places": [
            {"name": "패션5", "category": "베이커리", "address": "서울 용산구 한남동", "url": ""},
            {"name": "오프더레코드", "category": "카페", "address": "서울 용산구 한남동", "url": ""},
            {"name": "고사우스", "category": "다이닝", "address": "서울 용산구 한남동", "url": ""},
        ],
    },
    "수": {
        "name": "성수동",
        "tag": "트렌드의 흐름",
        "why": "물의 기운이 흐르는 달, 트렌드가 모이는 성수동에서 새로운 경험을 함께 흘려보내기 좋아요.",
        "places": [
            {"name": "어니언 성수", "category": "카페", "address": "서울 성동구 성수동", "url": ""},
            {"name": "대림창고", "category": "카페", "address": "서울 성동구 성수동", "url": ""},
            {"name": "소문난성수감자탕", "category": "맛집", "address": "서울 성동구 성수동", "url": ""},
        ],
    },
}


def neighborhood_of(element: str) -> dict:
    """오행 → {'element','name','tag','why','places'} (places는 카카오 키 없을 때 쓰는 폴백)."""
    nbh = NEIGHBORHOODS[element]
    return {"element": element, **nbh}
