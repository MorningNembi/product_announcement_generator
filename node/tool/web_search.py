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
    node_log("WEB SEARCH")
    # 1) 블로그 도메인만 포함하도록 TavilySearch 인스턴스 생성
    blog_domains = ["blog.naver.com", "blog.daum.net", "tistory.com"]
    tavily_tool = TavilySearch(include_domains=blog_domains, max_results=3)

    query = state["generation"]["product_lower_name"]
    search_query = f"{query} 장점"
    state["web_search_query"] = search_query

    # 2) 도메인 필터링 옵션을 기본으로 사용
    search_result = tavily_tool.search(
        query=search_query,
        format_output=False,
    )

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
