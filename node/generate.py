# node/generate.py

from langchain_core.prompts import PromptTemplate
from llm.factory import get_generator_client
from config import SUMMARIZER_TEMPLATE, node_log
from typing import Dict

# 1) LLM 클라이언트와 프롬프트 준비
llm = get_generator_client()
prompt_template = PromptTemplate.from_template(SUMMARIZER_TEMPLATE)


def generate(state: Dict) -> Dict:
    """
    LangGraph 노드: RAG로부터 받은 documents를
    Summarizer 프롬프트에 넣고 LLM으로 요약을 생성합니다.
    """
    node_log("GENERATE")
    docs = state["documents"]
    # <document> 태그로 wrapping
    context = "\n\n".join(
        f"<document><content>{doc.page_content}</content><source>{doc.metadata['source']}</source></document>"
        for doc in docs
    )
    # 프롬프트 포맷팅 및 호출
    prompt = prompt_template.format(context=context)
    summary = llm.chat(prompt)
    state["generation"] = summary
    # return state
    return {"generation": summary}
