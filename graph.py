from typing_extensions import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from node.tool.fetch_html import fetch_html_tool
from node.tool.vision_parser import vision_parser_tool
from node.tool.web_search import web_search_tool

from node.route_question import route_question
from node.clean_html import html_clean
from node.rag_retrieve import rag_retrieve

# from node.generate import generate
from node.rewrite_retrieve_query import (
    transform_retrieve_query,
    transform_web_search_query,
)
from node.groundness_check import (
    grade_generation_v_documents_and_annc_parser,
    grade_generation_v_documents_and_desc_gen,
)
from node.product_annc_parser import product_annc_parser
from node.product_desc_gen import product_desc_gen


class GraphState(TypedDict):
    url: Annotated[str, "url"]
    html: Annotated[list, "HTML"]
    retriever_query: Annotated[str, "retriever_query"]
    web_search_query: Annotated[str, "web_search_query"]
    documents: Annotated[list, "docs"]
    web_search: Annotated[list, "web_search"]
    generation: Annotated[str, "summary"]


# 그래프 상태 초기화
workflow = StateGraph(GraphState)

# 노드 정의
workflow.add_node("fetch_html_tool", fetch_html_tool)  # HTML 문서 가져오기
workflow.add_node("vision_parser_tool", vision_parser_tool)
workflow.add_node("web_search_tool", web_search_tool)  # 웹 서칭

workflow.add_node("clean_html", html_clean)  # HTML 문서 정리
workflow.add_node("rag_retrieve", rag_retrieve)  # RAG 문서 검색

workflow.add_node("product_annc_parser", product_annc_parser)  # 상품 정보 파싱
workflow.add_node("product_desc_gen", product_desc_gen)  # 상품 설명 생성
workflow.add_node("transform_retrieve_query", transform_retrieve_query)  # 질의 재작성
workflow.add_node(
    "transform_web_search_query", transform_web_search_query
)  # 질의 재작성
# workflow.add_node("generate", generate)  # generate

# 엣지 정의
workflow.add_conditional_edges(
    START,
    route_question,
    {
        "fetch_html_tool": "fetch_html_tool",
        "vision_parser_tool": "fetch_html_tool",  # vision_parser_tool 미구현
    },
)

workflow.add_edge("fetch_html_tool", "clean_html")
workflow.add_edge("clean_html", "rag_retrieve")
workflow.add_edge("vision_parser_tool", "rag_retrieve")

workflow.add_edge("rag_retrieve", "product_annc_parser")

workflow.add_conditional_edges(
    "product_annc_parser",
    grade_generation_v_documents_and_annc_parser,
    {
        "hallucination": "transform_retrieve_query",
        "relevant": "web_search_tool",
    },
)
workflow.add_edge("transform_retrieve_query", "rag_retrieve")
workflow.add_edge("web_search_tool", "product_desc_gen")

workflow.add_conditional_edges(
    "product_desc_gen",
    grade_generation_v_documents_and_desc_gen,
    {
        "hallucination": "transform_web_search_query",
        "relevant": END,
    },
)
workflow.add_edge("transform_web_search_query", "web_search_tool")

# 그래프 컴파일
app = workflow.compile(checkpointer=MemorySaver())
