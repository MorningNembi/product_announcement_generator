from langchain_teddynote.tools.tavily import TavilySearch
from langchain_core.documents import Document
from typing import Dict
from config import node_log

from langchain.schema import Document


def parse_search_dict(rec: dict) -> Document:
    title = rec.get("title", "")
    content = rec.get("content", "")
    url = rec.get("url", "")
    score = rec.get("score", None)

    # 제목과 내용만 page_content로 합치기
    page_content = f"{title}\n\n{content}"

    # URL은 source로, score가 있으면 metadata에 포함
    metadata = {"source": url}
    if score is not None:
        metadata["score"] = score

    return Document(page_content=page_content, metadata=metadata)


def web_search_tool(state: Dict) -> Dict:
    """
    ocr을 통해 추출한 상품명을 바탕으로 상품에 대한 정보를 서칭하는 도구
    """
    node_log("WEB SEARCH")
    # 검색 도구 생성
    tavily_tool = TavilySearch()
    parser = state["generation"]
    query = parser["product_lower_name"]
    search_query = f"{query} 리뷰"
    state["web_search_query"] = search_query
    # 다양한 파라미터를 사용한 검색 예제
    search_result = tavily_tool.search(
        query=search_query,  # 검색 쿼리
        max_results=3,  # 최대 검색 결과
        format_output=False,  # 결과 포맷팅
    )
    # 변환 수행
    state["web_search"] = [parse_search_dict(rec) for rec in search_result]

    return state


if __name__ == "__main__":
    # 테스트용 코드
    state = {}
    state["generation"] = {
        "product_name": "삼성 갤럭시 S23",
        "total_price": 1000000,
        "count": 1,
    }
    web_search_tool(state)
    print(state["web_search"])
