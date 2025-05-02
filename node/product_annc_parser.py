from langchain_core.prompts import PromptTemplate
from llm.factory import get_annc_parser_client
from config import PRODUCT_ANNC_PARCER_PROMPT, node_log
from typing import Dict
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser

# 1) LLM 클라이언트와 프롬프트 준비
llm = get_annc_parser_client()
prompt_template = PromptTemplate.from_template(PRODUCT_ANNC_PARCER_PROMPT)


class Topic(BaseModel):
    product_name: str = Field(description="메인 상품의 상품명")
    total_price: int = Field(description="메인 상품의 가격")
    count: int = Field(description="메인 상품의 개수(개수 단위가 붙은 숫자)")


def product_annc_parser(state: Dict) -> Dict:
    node_log("PRODUCT ANNOUNCEMENT PARSER")
    docs = state["documents"]
    context = "\n\n".join(
        f"<document><content>{doc.page_content}</content><source>{doc.metadata['source']}</source></document>"
        for doc in docs
    )

    # JsonOutputParser 설정
    parser = JsonOutputParser(pydantic_object=Topic)

    # 1) format_instructions를 먼저 바인딩 (partial)
    prompt_with_instructions = prompt_template.partial(
        format_instructions=parser.get_format_instructions()
    )

    # 2) context를 전달하여 최종 문자열 생성
    formatted_prompt = prompt_with_instructions.format(context=context)

    # 3) LLM 호출
    answer = llm.chat(formatted_prompt)
    text = getattr(answer, "content", answer)
    parsed: Topic = parser.parse(text)

    state["generation"] = parsed
    return state
