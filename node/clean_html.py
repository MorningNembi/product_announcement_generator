from bs4 import BeautifulSoup
from typing import Dict, Any
from config import node_log
import json


def html_clean(state: Dict[str, Any]) -> Dict[str, Any]:
    node_log("CLEANING HTML TAG AND KEEPING ONLY PRODUCT INFO")

    raw_html = (
        state["page"][0].page_content
        if isinstance(state["page"], list) and hasattr(state["page"][0], "page_content")
        else state["page"]
    )
    # html 테그 제거?
    soup = BeautifulSoup(raw_html, "html.parser")
    state["page"] = soup.get_text(separator="\n", strip=True)
    # 2) 화이트리스트에 있는 요소만 개별적으로 추출
    pieces = []

    # 2-1) <title> 텍스트
    if soup.title and soup.title.string:
        pieces.append(soup.title.string.strip())

    # 2-2) meta description, og:description
    for sel in ["meta[name='description']", "meta[property='og:description']"]:
        tag = soup.select_one(sel)
        if tag and tag.get("content"):
            pieces.append(tag["content"].strip())

    # 2-3) og:title
    tag = soup.select_one("meta[property='og:title']")
    if tag and tag.get("content"):
        pieces.append(tag["content"].strip())

    # 2-4) JSON 페이로드 (script#data)
    data_tag = soup.select_one("script#data")
    if data_tag and data_tag.string:
        try:
            obj = json.loads(data_tag.string)
            # 예: prdNo, price, category 같은 키만 뽑기
            for key in ["prdNo", "price", "content_category"]:
                if key in obj:
                    pieces.append(f"{key}: {obj[key]}")
        except json.JSONDecodeError:
            pass

    # 3) 필요하면 다른 셀렉터로 가격·리뷰·평점 등을 더 추출
    # 예: pieces.append(soup.select_one(".price").get_text(strip=True))

    # 4) pieces를 줄바꿈으로 합쳐 Document로 래핑
    combined = "\n".join(pieces)
    state["page_meta"] = combined

    return state
