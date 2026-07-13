"""ssod-saju-engine 참조 HTTP API 서버.

엔진(saju 패키지)을 HTTP로 얇게 노출하는 참조 구현이다. 언어 무관하게
사주 계산을 쓰고 싶을 때 이 서버를 그대로 띄우거나 사본으로 삼으면 된다.

    pip install "ssod-saju-engine[server]"
    uvicorn server.main:app --reload   # http://127.0.0.1:8000/docs
"""
