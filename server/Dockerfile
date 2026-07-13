# 참조 API 서버 컨테이너 이미지.
#   docker build -f server/Dockerfile -t ssod-saju-api .
#   docker run -p 8000:8000 ssod-saju-api   # http://localhost:8000/docs
FROM python:3.12-slim

WORKDIR /app

# 비루트 사용자로 실행(보안)
RUN groupadd -r app && useradd -r -g app -s /sbin/nologin app

COPY pyproject.toml README.md LICENSE ./
COPY saju ./saju
COPY server ./server

RUN pip install --no-cache-dir ".[server]"

USER app

EXPOSE 8000
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]
