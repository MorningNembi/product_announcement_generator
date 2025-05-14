import re
from bs4 import BeautifulSoup
from typing import Dict, Any
from config import node_log
import json


def html_clean(state: Dict[str, Any]) -> Dict[str, Any]:
    node_log("CLEANING HTML TAG AND KEEPING ONLY PRODUCT INFO")

    # 1) 원본 HTML 가져오기
    raw_html = (
        state["page"][0].page_content
        if isinstance(state["page"], list) and hasattr(state["page"][0], "page_content")
        else state["page"]
    )

    # 2) BeautifulSoup으로 태그 제거 & 순수 텍스트 저장
    soup = BeautifulSoup(raw_html, "html.parser")
    state["page"] = soup.get_text(separator="\n", strip=True)

    pieces: list[str] = []

    # 3) <title>, meta.description, og:description, og:title
    if soup.title and soup.title.string:
        pieces.append(soup.title.string.strip())
    for sel in ("meta[name='description']", "meta[property='og:description']"):
        tag = soup.select_one(sel)
        if tag and tag.has_attr("content"):
            pieces.append(tag["content"].strip())
    tag = soup.select_one("meta[property='og:title']")
    if tag and tag.has_attr("content"):
        pieces.append(tag["content"].strip())

    # 4) script#data 내부 JSON 페이로드 (견본)
    data_tag = soup.select_one("script#data")
    if data_tag and data_tag.string:
        try:
            obj = json.loads(data_tag.string)
            for key in ("prdNo", "price", "content_category"):
                if key in obj:
                    pieces.append(f"{key}: {obj[key]}")
        except json.JSONDecodeError:
            pass

    # 5) 주요 JSON 키 패턴으로 가격 검색
    # 키(name)와 값(value)를 그룹으로 캡처
    pattern_kv = r'"([^"]*price[^"]*)"\s*:\s*([0-9]+(?:\.[0-9]+)?)'
    matches_kv = re.findall(pattern_kv, raw_html, flags=re.IGNORECASE)

    # 값이 0인 항목은 건너뛰고, '키: 값,' 형태로 리스트 생성
    for key, val in matches_kv:
        if int(val) != 0:
            pieces.append(f"{key}: {val}")

    # 7) pieces를 state["page_meta"]에 담아서 Return
    state["page_meta"] = "\n".join(pieces)
    return state
