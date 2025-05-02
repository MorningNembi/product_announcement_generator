# node/route_question.py

import json
from typing import Literal, Dict
from pydantic import BaseModel, Field, ValidationError

from llm.factory import get_router_client
from config import ROUTER_PROMPT, node_log


# Pydantic 데이터모델
class RouteQuery(BaseModel):
    datasource: Literal[
        "fetch_html_tool", "coopang_html_tool", "vision_model_parser"
    ] = Field(..., description="어떤 도구로 라우팅할지 선택합니다.")


# LLM 클라이언트
llm = get_router_client()


def route_question(state: Dict) -> str:
    node_log("ROUTE QUESTION")

    # 1) 프롬프트: "반드시 JSON 형식으로만" 출력하도록 명시
    prompt = (
        ROUTER_PROMPT.strip()
        + "\n\n"
        + "URL: "
        + state["url"]
        + "\n\n"
        + "== 응답 형식 (JSON) ==\n"
        + '{"datasource": "<fetch_html_tool|coopang_html_tool|vision_model_parser>"}'
    )

    # 2) LLM 호출 → raw JSON string or free text
    raw_output = llm.chat(prompt).strip()

    # 3) JSON 파싱 시도
    try:
        result = RouteQuery.parse_raw(raw_output)
        ds = result.datasource
    except (json.JSONDecodeError, ValidationError):
        # 파싱 실패하면 간단 룰베이스로 fallback
        url = state["url"]
        if "coupang.com" in url:
            ds = "coopang_html_tool"
        elif url.lower().endswith((".jpg", ".png", ".jpeg", ".gif")):
            ds = "vision_model_parser"
        else:
            ds = "fetch_html_tool"

    node_log(f"ROUTE TO {ds.upper()}")
    return ds
