# node/route_question.py
from typing import Literal, Dict
from pydantic import BaseModel, Field

from llm.factory import get_router_client
from config import ROUTER_PROMPT, node_log


# Pydantic 데이터모델
class RouteQuery(BaseModel):
    datasource: Literal["fetch_html_tool", "fetch_coupang_tool", "parse_image_text"] = (
        Field(..., description="어떤 도구로 라우팅할지 선택합니다.")
    )


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
        + "== 응답 형식 ==\n"
        + "fetch_html_tool, fetch_coupang_tool, parse_image_text\n"
    )

    # 2) LLM 호출 → raw JSON string or free text
    ds = llm.chat(prompt).strip()
    # 이후 안정성을 위해 답변에서 필요한 부분만 파싱하는 로직 추가
    # print(ds)
    return ds
