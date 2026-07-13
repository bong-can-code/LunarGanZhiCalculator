"""사주 계산 엔진을 노출하는 참조 FastAPI 앱.

엔드포인트:
  POST /calculate  — 한 사람의 사주 4주 + 명리 분석
  POST /compat     — 2인(연인) 또는 3~4인(팀) 궁합
  GET  /health     — 헬스체크

FastAPI가 /docs(Swagger)·/openapi.json 을 자동 생성하므로 어떤 언어에서도
스키마를 보고 호출할 수 있다.
"""

from __future__ import annotations

from typing import Literal, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from saju import calculate_saju
from saju.compat import couple_compat, team_compat, zodiac_of

app = FastAPI(
    title="ssod-saju-engine API",
    version="0.1.0",
    description="한국 사주(四柱) 간지·명리 계산 엔진의 참조 HTTP API. Apache-2.0.",
)


class SajuRequest(BaseModel):
    year: int = Field(..., examples=[1990])
    month: int = Field(..., ge=1, le=12, examples=[5])
    day: int = Field(..., ge=1, le=31, examples=[15])
    hour: Optional[int] = Field(None, ge=0, le=23, description="0~23시. None이면 시주 생략(시간 모름).")
    is_lunar: bool = Field(False, description="입력이 음력이면 True")
    is_leap_month: bool = Field(False, description="음력 윤달이면 True")
    gender: Optional[Literal["male", "female"]] = Field(
        None, description="주어지면 대운(순행/역행·대운수)도 계산"
    )


class CompatRequest(BaseModel):
    people: list[SajuRequest] = Field(
        ..., min_length=2, max_length=4, description="2인=연인 궁합, 3~4인=팀 궁합"
    )


def _calc(req: SajuRequest) -> dict:
    try:
        return calculate_saju(
            req.year, req.month, req.day, req.hour,
            is_lunar=req.is_lunar, is_leap_month=req.is_leap_month, gender=req.gender,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/calculate", summary="사주 4주 + 명리 분석 계산")
def calculate(req: SajuRequest) -> dict:
    return _calc(req)


@app.post("/compat", summary="궁합 계산 (2인 연인 / 3~4인 팀)")
def compat(req: CompatRequest) -> dict:
    sajus = [_calc(p) for p in req.people]
    if len(sajus) == 2:
        return {"mode": "couple", "zodiacs": [zodiac_of(s) for s in sajus], **couple_compat(sajus[0], sajus[1])}
    return {"mode": "team", "zodiacs": [zodiac_of(s) for s in sajus], **team_compat(sajus)}


@app.get("/health", summary="헬스체크")
def health() -> dict:
    return {"status": "ok"}
