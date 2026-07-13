# 참조 API 서버 컨테이너 이미지.
#   docker build -f server/Dockerfile -t ssod-saju-api .
#   docker run -p 8000:8000 ssod-saju-api   # http://localhost:8000/docs
FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY saju ./saju
COPY server ./server

RUN pip install --no-cache-dir ".[server]"

EXPOSE 8000
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]
